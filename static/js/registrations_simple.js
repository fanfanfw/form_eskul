// JavaScript SIMPLE untuk registrations - version 2
$(document).ready(function() {
    console.log('🚀 Registrations page loaded - Simple version');
    loadAndDisplayData();
});

async function loadAndDisplayData() {
    try {
        console.log('📡 Fetching data from API...');
        
        const response = await fetch('/api/registrations');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Data received:', data);
        
        if (!data.registrations || !Array.isArray(data.registrations)) {
            throw new Error('Invalid data format');
        }
        
        // SIMPLE counting - no complex logic
        const allStudents = data.registrations;
        const totalSiswa = allStudents.length;
        
        // Count students with eskul - VERY SIMPLE CHECK
        let sudahDaftarCount = 0;
        allStudents.forEach(student => {
            if (student.nama_eskul && student.nama_eskul !== null && student.nama_eskul.trim() !== '') {
                sudahDaftarCount++;
                console.log(`✅ Found registered student: ${student.nama} -> ${student.nama_eskul}`);
            }
        });
        
        const belumDaftar = totalSiswa - sudahDaftarCount;
        
        // Count unique classes
        const uniqueClasses = [...new Set(allStudents.map(s => s.kelas).filter(k => k))];
        const totalKelas = uniqueClasses.length;
        
        console.log('📊 FINAL COUNTS:');
        console.log(`   Total: ${totalSiswa}`);
        console.log(`   Sudah Daftar: ${sudahDaftarCount}`);
        console.log(`   Belum Daftar: ${belumDaftar}`);
        console.log(`   Total Kelas: ${totalKelas}`);
        
        // Update display IMMEDIATELY
        document.getElementById('totalSiswa').textContent = totalSiswa;
        document.getElementById('sudahDaftar').textContent = sudahDaftarCount;
        document.getElementById('belumDaftar').textContent = belumDaftar;
        document.getElementById('totalKelas').textContent = totalKelas;
        
        console.log('✅ Display updated');
        
        // Build table
        buildTable(allStudents);
        
    } catch (error) {
        console.error('❌ Error:', error);
        document.getElementById('loadingSpinner').innerHTML = `
            <div class="alert alert-danger">
                Error loading data: ${error.message}
            </div>
        `;
    }
}

function buildTable(students) {
    console.log('🏗️ Building table...');
    
    const tbody = document.querySelector('#registrationTable tbody');
    tbody.innerHTML = '';
    
    students.forEach(student => {
        const row = document.createElement('tr');
        
        // Determine eskul display
        let eskulDisplay = '<span class="badge bg-warning">Belum Daftar</span>';
        if (student.nama_eskul && student.nama_eskul.trim() !== '') {
            eskulDisplay = `<span class="badge bg-success">${student.nama_eskul}</span>`;
        }
        
        // Determine gender display
        let genderDisplay = '<span class="badge bg-secondary">-</span>';
        if (student.jeniskelamin === 'L') {
            genderDisplay = '<span class="badge bg-info">Laki-laki</span>';
        } else if (student.jeniskelamin === 'P') {
            genderDisplay = '<span class="badge bg-success">Perempuan</span>';
        }
        
        row.innerHTML = `
            <td>${student.nis || '-'}</td>
            <td>${student.nisn || '-'}</td>
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-user-circle me-2 text-primary"></i>
                    <strong>${student.nama || 'Nama tidak tersedia'}</strong>
                </div>
            </td>
            <td>${genderDisplay}</td>
            <td><span class="badge bg-secondary">${student.kelas || 'Tidak diketahui'}</span></td>
            <td>${eskulDisplay}</td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Initialize DataTable
    $('#registrationTable').DataTable({
        responsive: true,
        pageLength: 25,
        order: [[4, 'asc'], [2, 'asc']], // Sort by class, then name
        language: {
            search: "Cari:",
            lengthMenu: "Tampilkan _MENU_ data per halaman",
            info: "Menampilkan _START_ sampai _END_ dari _TOTAL_ data",
            infoEmpty: "Menampilkan 0 sampai 0 dari 0 data",
            infoFiltered: "(difilter dari _MAX_ total data)",
            paginate: {
                first: "Pertama",
                last: "Terakhir", 
                next: "Selanjutnya",
                previous: "Sebelumnya"
            },
            emptyTable: "Tidak ada data yang tersedia"
        }
    });
    
    // Show table and hide loading
    document.getElementById('loadingSpinner').style.display = 'none';
    document.getElementById('tableContainer').style.display = 'block';
    
    console.log('✅ Table built and displayed');
}

// Add export functions to window for buttons
window.exportToCSV = function() {
    console.log('📄 Exporting to CSV...');
    
    try {
        // Get the raw data instead of the formatted table data
        fetch('/api/registrations')
            .then(response => response.json())
            .then(data => {
                // Create CSV header
                let csv = 'NIS,NISN,Nama Siswa,Jenis Kelamin,Kelas,Ekstrakurikuler\n';
                
                // Process each student record
                data.registrations.forEach(student => {
                    const nis = (student.nis || '').toString().replace(/,/g, ';');
                    const nisn = (student.nisn || '').toString().replace(/,/g, ';');
                    const nama = (student.nama || 'Nama tidak tersedia').toString().replace(/,/g, ';');
                    
                    let jenisKelamin = '';
                    if (student.jeniskelamin === 'L') {
                        jenisKelamin = 'Laki-laki';
                    } else if (student.jeniskelamin === 'P') {
                        jenisKelamin = 'Perempuan';
                    } else {
                        jenisKelamin = 'Tidak diketahui';
                    }
                    
                    const kelas = (student.kelas || 'Tidak diketahui').toString().replace(/,/g, ';');
                    
                    let eskul = 'Belum Daftar';
                    if (student.nama_eskul && student.nama_eskul.trim() !== '') {
                        eskul = student.nama_eskul.toString().replace(/,/g, ';');
                    }
                    
                    // Add row to CSV
                    csv += `"${nis}","${nisn}","${nama}","${jenisKelamin}","${kelas}","${eskul}"\n`;
                });
                
                // Create and download file
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                
                if (link.download !== undefined) {
                    const url = URL.createObjectURL(blob);
                    link.setAttribute('href', url);
                    
                    // Create filename with current date
                    const today = new Date();
                    const dateStr = today.getFullYear() + '-' + 
                                  String(today.getMonth() + 1).padStart(2, '0') + '-' + 
                                  String(today.getDate()).padStart(2, '0');
                    
                    link.setAttribute('download', `registrasi_eskul_${dateStr}.csv`);
                    link.style.visibility = 'hidden';
                    
                    // Add to page, click, and remove
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    console.log('✅ CSV file downloaded successfully');
                    showSuccessMessage(`File CSV berhasil didownload! (${data.registrations.length} records)`);
                    
                    // Clean up URL
                    setTimeout(() => URL.revokeObjectURL(url), 1000);
                } else {
                    throw new Error('Browser tidak mendukung download otomatis');
                }
            })
            .catch(error => {
                console.error('❌ Error fetching data for export:', error);
                showErrorMessage('Gagal mengambil data untuk export: ' + error.message);
            });
            
    } catch (error) {
        console.error('❌ Error exporting CSV:', error);
        showErrorMessage('Gagal export CSV: ' + error.message);
    }
};

window.printTable = function() {
    console.log('🖨️ Printing table...');
    
    try {
        // Get current date for header
        const currentDate = new Date().toLocaleDateString('id-ID', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        // Get table data
        const table = document.getElementById('registrationTable');
        const tableClone = table.cloneNode(true);
        
        // Remove any buttons or interactive elements from the clone
        const buttons = tableClone.querySelectorAll('button, .btn');
        buttons.forEach(btn => btn.remove());
        
        // Create print content
        const printContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Data Registrasi Ekstrakurikuler</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 20px;
                        font-size: 12px;
                    }
                    table { 
                        border-collapse: collapse; 
                        width: 100%; 
                        margin-top: 20px;
                    }
                    th, td { 
                        border: 1px solid #ddd; 
                        padding: 8px; 
                        text-align: left; 
                    }
                    th { 
                        background-color: #f2f2f2; 
                        font-weight: bold;
                    }
                    h1 { 
                        text-align: center; 
                        color: #333; 
                        margin-bottom: 10px;
                    }
                    .header-info {
                        text-align: center;
                        margin-bottom: 20px;
                        color: #666;
                    }
                    .badge {
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-size: 10px;
                    }
                    .bg-success { background-color: #d4edda; color: #155724; }
                    .bg-warning { background-color: #fff3cd; color: #856404; }
                    .bg-info { background-color: #d1ecf1; color: #0c5460; }
                    .bg-secondary { background-color: #e2e3e5; color: #383d41; }
                    @media print {
                        body { margin: 0; }
                        .no-print { display: none; }
                    }
                </style>
            </head>
            <body>
                <h1>Data Registrasi Ekstrakurikuler</h1>
                <div class="header-info">
                    <p>Tanggal Cetak: ${currentDate}</p>
                    <p>Total Data: ${document.getElementById('totalSiswa').textContent} siswa</p>
                </div>
                ${tableClone.outerHTML}
                <div style="margin-top: 30px; font-size: 10px; color: #666;">
                    <p>Dicetak dari Form Eskul Siswa - ${window.location.origin}</p>
                </div>
            </body>
            </html>
        `;
        
        // Open print window
        const printWindow = window.open('', '_blank', 'width=800,height=600');
        printWindow.document.write(printContent);
        printWindow.document.close();
        
        // Wait for content to load then print
        printWindow.onload = function() {
            printWindow.focus();
            printWindow.print();
        };
        
        console.log('✅ Print dialog opened');
        
    } catch (error) {
        console.error('❌ Error printing:', error);
        showErrorMessage('Gagal print: ' + error.message);
    }
};

window.refreshData = function() {
    console.log('🔄 Refreshing data...');
    
    // Show loading
    document.getElementById('tableContainer').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'block';
    
    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#registrationTable')) {
        $('#registrationTable').DataTable().destroy();
    }
    
    // Clear table body
    document.querySelector('#registrationTable tbody').innerHTML = '';
    
    // Reload data
    setTimeout(() => {
        loadAndDisplayData();
    }, 500);
};

// Helper functions for messages
function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'danger');
}

function showMessage(message, type) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}
