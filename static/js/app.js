// JavaScript untuk Form Eskul
document.addEventListener('DOMContentLoaded', function() {
    const kelasSelect = document.getElementById('kelasSelect');
    const siswaSelect = document.getElementById('siswaSelect');
    const eskulSelect = document.getElementById('eskulSelect');
    const submitBtn = document.getElementById('submitBtn');
    const eskulForm = document.getElementById('eskulForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const alertContainer = document.getElementById('alertContainer');

    // Load initial data
    loadKelas();
    loadEskul();

    // Event listeners
    kelasSelect.addEventListener('change', handleKelasChange);
    siswaSelect.addEventListener('change', handleSiswaChange);
    eskulForm.addEventListener('submit', handleFormSubmit);

    // Fungsi untuk menampilkan alert
    function showAlert(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
        
        // Scroll to top to show alert
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Fungsi untuk load daftar kelas
    async function loadKelas() {
        try {
            const response = await fetch('/api/kelas');
            const data = await response.json();
            
            kelasSelect.innerHTML = '<option value="">-- Pilih Kelas --</option>';
            
            data.kelas.forEach(kelas => {
                const option = document.createElement('option');
                option.value = kelas;
                option.textContent = kelas;
                kelasSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading kelas:', error);
            showAlert('Gagal memuat daftar kelas', 'danger');
        }
    }

    // Data eskul yang hanya untuk kelas 3 ke atas
    const restrictedEskul = ['Pencak Silat', 'Futsal', 'Angklung'];
    
    // Fungsi untuk load daftar eskul
    async function loadEskul() {
        try {
            const response = await fetch('/api/eskul');
            const data = await response.json();
            
            // Simpan data eskul untuk filtering nanti
            window.allEskul = data.eskul;
            
            // Load semua eskul pertama kali (akan di-filter saat kelas dipilih)
            populateEskulOptions(data.eskul, '');
            
        } catch (error) {
            console.error('Error loading eskul:', error);
            showAlert('Gagal memuat daftar ekstrakurikuler', 'danger');
        }
    }
    
    // Fungsi untuk mengisi options eskul berdasarkan kelas
    function populateEskulOptions(eskulList, selectedKelas) {
        eskulSelect.innerHTML = '<option value="">-- Pilih Ekstrakurikuler --</option>';
        
        // Cek apakah kelas 1 atau kelas 2
        const isKelas1or2 = selectedKelas && (selectedKelas.toLowerCase().includes('kelas 1') || selectedKelas.toLowerCase().includes('kelas 2'));
        
        eskulList.forEach(eskul => {
            const option = document.createElement('option');
            option.value = eskul.id;
            option.textContent = eskul.nama_eskul;
            
            // Jika kelas 1 atau 2 dan eskul adalah yang dibatasi, disable option
            if (isKelas1or2 && restrictedEskul.includes(eskul.nama_eskul)) {
                option.disabled = true;
                option.textContent += ' (Hanya untuk kelas 3 ke atas)';
                option.style.color = '#999';
            }
            
            eskulSelect.appendChild(option);
        });
    }

    // Handler untuk perubahan kelas
    async function handleKelasChange() {
        const selectedKelas = kelasSelect.value;
        
        // Reset siswa dropdown
        siswaSelect.innerHTML = '<option value="">-- Loading... --</option>';
        siswaSelect.disabled = true;
        eskulSelect.disabled = true;
        submitBtn.disabled = true;
        
        if (!selectedKelas) {
            siswaSelect.innerHTML = '<option value="">-- Pilih kelas terlebih dahulu --</option>';
            // Reset eskul options juga
            if (window.allEskul) {
                populateEskulOptions(window.allEskul, '');
            }
            return;
        }

        // Update eskul options berdasarkan kelas yang dipilih
        if (window.allEskul) {
            populateEskulOptions(window.allEskul, selectedKelas);
            
            // Tampilkan peringatan jika kelas 1 atau 2
            const isKelas1or2Warning = selectedKelas.toLowerCase().includes('kelas 1') || selectedKelas.toLowerCase().includes('kelas 2');
            if (isKelas1or2Warning) {
                showAlert('Perhatian: Kelas 1 dan kelas 2 tidak dapat memilih eskul Pencak Silat, Futsal, dan Angklung (hanya untuk kelas 3 ke atas)', 'warning');
            }
        }

        try {
            const response = await fetch(`/api/siswa/${encodeURIComponent(selectedKelas)}`);
            const data = await response.json();
            
            siswaSelect.innerHTML = '<option value="">-- Pilih Siswa --</option>';
            
            data.siswa.forEach(siswa => {
                const option = document.createElement('option');
                option.value = siswa.id;
                option.textContent = siswa.nama; // Hanya tampilkan nama tanpa NIS
                siswaSelect.appendChild(option);
            });
            
            siswaSelect.disabled = false;
            
        } catch (error) {
            console.error('Error loading siswa:', error);
            showAlert('Gagal memuat daftar siswa', 'danger');
            siswaSelect.innerHTML = '<option value="">-- Error loading siswa --</option>';
        }
    }

    // Handler untuk perubahan siswa
    function handleSiswaChange() {
        const selectedSiswa = siswaSelect.value;
        
        if (selectedSiswa) {
            eskulSelect.disabled = false;
            updateSubmitButton();
        } else {
            eskulSelect.disabled = true;
            submitBtn.disabled = true;
        }
    }

    // Update status tombol submit
    function updateSubmitButton() {
        const kelasSelected = kelasSelect.value;
        const siswaSelected = siswaSelect.value;
        const eskulSelected = eskulSelect.value;
        
        submitBtn.disabled = !(kelasSelected && siswaSelected && eskulSelected);
    }

    // Enable submit button when eskul is selected
    eskulSelect.addEventListener('change', updateSubmitButton);

    // Handler untuk submit form
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const siswaId = siswaSelect.value;
        const eskulId = eskulSelect.value;
        const selectedKelas = kelasSelect.value;
        
        if (!siswaId || !eskulId) {
            showAlert('Mohon lengkapi semua field', 'danger');
            return;
        }

        // Validasi eskul berdasarkan kelas
        const isKelas1or2Submit = selectedKelas && (selectedKelas.toLowerCase().includes('kelas 1') || selectedKelas.toLowerCase().includes('kelas 2'));
        if (isKelas1or2Submit && window.allEskul) {
            const selectedEskul = window.allEskul.find(eskul => eskul.id == eskulId);
            if (selectedEskul && restrictedEskul.includes(selectedEskul.nama_eskul)) {
                showAlert('Siswa kelas 1 dan kelas 2 tidak dapat memilih ' + selectedEskul.nama_eskul + '. Silakan pilih ekstrakurikuler lain.', 'danger');
                return;
            }
        }

        // Show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Memproses...';
        loadingSpinner.style.display = 'block';

        try {
            const formData = new FormData();
            formData.append('siswa_id', siswaId);
            formData.append('eskul_id', eskulId);

            const response = await fetch('/api/submit', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showAlert(result.message, 'success');
                
                // Reset form
                eskulForm.reset();
                siswaSelect.innerHTML = '<option value="">-- Pilih kelas terlebih dahulu --</option>';
                siswaSelect.disabled = true;
                eskulSelect.disabled = true;
                submitBtn.disabled = true;
                
                // Add success animation
                document.querySelector('.card').style.transform = 'scale(1.02)';
                setTimeout(() => {
                    document.querySelector('.card').style.transform = 'scale(1)';
                }, 300);
                
            } else {
                showAlert(result.detail || 'Terjadi kesalahan saat menyimpan data', 'danger');
            }

        } catch (error) {
            console.error('Error submitting form:', error);
            showAlert('Terjadi kesalahan koneksi', 'danger');
        } finally {
            // Hide loading
            loadingSpinner.style.display = 'none';
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Daftarkan ke Eskul';
            updateSubmitButton();
        }
    }

    // Add smooth transitions
    function addSmoothTransitions() {
        const selects = document.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('focus', function() {
                this.style.transform = 'scale(1.02)';
            });
            
            select.addEventListener('blur', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }

    // Initialize smooth transitions
    addSmoothTransitions();

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl + Enter to submit form
        if (e.ctrlKey && e.key === 'Enter' && !submitBtn.disabled) {
            handleFormSubmit(e);
        }
        
        // Escape to reset form
        if (e.key === 'Escape') {
            if (confirm('Reset form?')) {
                eskulForm.reset();
                siswaSelect.innerHTML = '<option value="">-- Pilih kelas terlebih dahulu --</option>';
                siswaSelect.disabled = true;
                eskulSelect.disabled = true;
                submitBtn.disabled = true;
            }
        }
    });

    // Add tooltips for better UX
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        initTooltips();
    }
});
