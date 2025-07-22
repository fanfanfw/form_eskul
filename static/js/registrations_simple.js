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
    // Simple CSV export logic here
};

window.printTable = function() {
    console.log('🖨️ Printing table...');
    window.print();
};

window.refreshData = function() {
    console.log('🔄 Refreshing data...');
    location.reload();
};
