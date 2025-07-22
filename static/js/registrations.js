// JavaScript untuk halaman registrasi
$(document).ready(function() {
    loadRegistrations();

    async function loadRegistrations() {
        try {
            const response = await fetch('/api/registrations');
            const data = await response.json();
            
            populateTable(data.registrations);
            updateSummary(data.registrations);
            
        } catch (error) {
            console.error('Error loading registrations:', error);
            showError('Gagal memuat data registrasi');
        }
    }

    function populateTable(registrations) {
        const tbody = $('#registrationTable tbody');
        tbody.empty();

        registrations.forEach(reg => {
            // Handle null values properly
            const nisValue = reg.nis || '-';
            const nisnValue = reg.nisn || '-';
            const namaValue = reg.nama || 'Nama tidak tersedia';
            const jenisKelaminValue = reg.jeniskelamin || 'Tidak diketahui';
            const kelasValue = reg.kelas || 'Tidak diketahui';
            
            const eskulText = reg.nama_eskul || '<span class="badge bg-warning">Belum Daftar</span>';
            
            const row = `
                <tr>
                    <td>${nisValue}</td>
                    <td>${nisnValue}</td>
                    <td>
                        <div class="d-flex align-items-center">
                            <i class="fas fa-user-circle me-2 text-primary"></i>
                            <strong>${namaValue}</strong>
                        </div>
                    </td>
                    <td>
                        <span class="badge ${jenisKelaminValue === 'L' ? 'bg-info' : jenisKelaminValue === 'P' ? 'bg-success' : 'bg-secondary'}">
                            ${jenisKelaminValue === 'L' ? 'Laki-laki' : jenisKelaminValue === 'P' ? 'Perempuan' : 'Tidak diketahui'}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-secondary">${kelasValue}</span>
                    </td>
                    <td>${eskulText}</td>
                </tr>
            `;
            tbody.append(row);
        });

        // Initialize DataTable
        $('#registrationTable').DataTable({
            responsive: true,
            pageLength: 25,
            order: [[4, 'asc'], [2, 'asc']], // Sort by kelas, then nama
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
            },
            columnDefs: [
                { orderable: false, targets: [5] } // Disable sorting for eskul column
            ]
        });

        // Hide loading and show table
        $('#loadingSpinner').hide();
        $('#tableContainer').show();
    }

    function updateSummary(registrations) {
        // Filter out any invalid registrations and handle nulls
        const validRegistrations = registrations.filter(reg => reg && reg.nama);
        
        const totalSiswa = validRegistrations.length;
        const sudahDaftar = validRegistrations.filter(reg => reg.nama_eskul && reg.nama_eskul.trim() !== '').length;
        const belumDaftar = totalSiswa - sudahDaftar;
        
        // Get unique classes, filtering out null/undefined values
        const validKelas = validRegistrations
            .map(reg => reg.kelas)
            .filter(kelas => kelas && kelas.trim() !== '');
        const totalKelas = [...new Set(validKelas)].length;

        // Update the display with proper number handling
        $('#totalSiswa').text(totalSiswa || 0);
        $('#sudahDaftar').text(sudahDaftar || 0);
        $('#belumDaftar').text(belumDaftar || 0);
        $('#totalKelas').text(totalKelas || 0);

        // Add animation to numbers
        animateNumbers();
    }

    function animateNumbers() {
        $('.card h2').each(function() {
            const $this = $(this);
            const finalValue = parseInt($this.text());
            
            // Only animate if we have a valid number
            if (!isNaN(finalValue) && finalValue >= 0) {
                $this.text('0');
                
                $({ counter: 0 }).animate({ counter: finalValue }, {
                    duration: 1500,
                    easing: 'swing',
                    step: function() {
                        $this.text(Math.ceil(this.counter));
                    }
                });
            } else {
                $this.text('0');
            }
        });
    }

    function showError(message) {
        $('#loadingSpinner').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `);
    }

    // Add export functionality
    function addExportButtons() {
        const buttonsHtml = `
            <div class="mb-3">
                <button class="btn btn-success me-2" onclick="exportToCSV()">
                    <i class="fas fa-file-csv me-1"></i> Export CSV
                </button>
                <button class="btn btn-primary me-2" onclick="printTable()">
                    <i class="fas fa-print me-1"></i> Print
                </button>
                <button class="btn btn-info" onclick="refreshData()">
                    <i class="fas fa-sync-alt me-1"></i> Refresh
                </button>
            </div>
        `;
        
        $('#tableContainer').prepend(buttonsHtml);
    }

    // Export to CSV function
    window.exportToCSV = function() {
        const table = $('#registrationTable').DataTable();
        const data = table.rows({ search: 'applied' }).data().toArray();
        
        let csv = 'NIS,NISN,Nama,Jenis Kelamin,Kelas,Ekstrakurikuler\n';
        
        data.forEach(row => {
            const cleanRow = row.map(cell => {
                // Remove HTML tags and clean data, handle null values
                let cleanCell = '';
                if (cell === null || cell === undefined || cell === 'null') {
                    cleanCell = '-';
                } else {
                    cleanCell = String(cell).replace(/<[^>]*>/g, '').replace(/,/g, ';');
                }
                return `"${cleanCell}"`;
            });
            csv += cleanRow.join(',') + '\n';
        });
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `registrasi_eskul_${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    // Print function
    window.printTable = function() {
        const printContent = `
            <html>
                <head>
                    <title>Data Registrasi Ekstrakurikuler</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                        h1 { text-align: center; color: #333; }
                    </style>
                </head>
                <body>
                    <h1>Data Registrasi Ekstrakurikuler</h1>
                    <p>Tanggal: ${new Date().toLocaleDateString('id-ID')}</p>
                    ${$('#registrationTable')[0].outerHTML}
                </body>
            </html>
        `;
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(printContent);
        printWindow.document.close();
        printWindow.print();
    };

    // Refresh data function
    window.refreshData = function() {
        $('#registrationTable').DataTable().destroy();
        $('#tableContainer').hide();
        $('#loadingSpinner').show();
        loadRegistrations();
    };

    // Add export buttons after table is loaded
    setTimeout(() => {
        if ($('#registrationTable').length) {
            addExportButtons();
        }
    }, 2000);
});
