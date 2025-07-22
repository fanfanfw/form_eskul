// Fungsi untuk test API registrations secara langsung
async function testRegistrationsAPI() {
    try {
        console.log('Testing /api/registrations endpoint...');
        
        const response = await fetch('/api/registrations');
        const data = await response.json();
        
        console.log('API Response:', data);
        console.log('Total records:', data.registrations.length);
        
        // Check for students with eskul
        const withEskul = data.registrations.filter(reg => {
            return reg.nama_eskul && 
                   reg.nama_eskul !== null && 
                   reg.nama_eskul !== 'null' && 
                   reg.nama_eskul.toString().trim() !== '';
        });
        
        console.log('Students with eskul:', withEskul.length);
        console.log('Students with eskul details:', withEskul);
        
        // Sample first few records
        console.log('First 5 records:');
        data.registrations.slice(0, 5).forEach((reg, index) => {
            console.log(`${index + 1}. ${reg.nama} - Eskul: "${reg.nama_eskul}" (type: ${typeof reg.nama_eskul})`);
        });
        
    } catch (error) {
        console.error('Error testing API:', error);
    }
}

// Jalankan test jika di browser console
if (typeof window !== 'undefined') {
    window.testRegistrationsAPI = testRegistrationsAPI;
    console.log('Run testRegistrationsAPI() in console to debug');
}
