let page = 1;
let pages = 1;
let pageSize = 25;
let options = { kelas: [], eskul: [] };

const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(
  /[&<>"']/g,
  character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character],
);

async function api(url, init) {
  const response = await fetch(url, init);
  const data = await response.json().catch(() => ({}));
  if (response.status === 401) {
    location = '/registrations';
    throw Error('Sesi berakhir');
  }
  if (!response.ok) throw Error(data.detail || 'Permintaan gagal');
  return data;
}

function params(includePage = true) {
  const query = new URLSearchParams();
  [
    ['search', $('search').value],
    ['kelas', $('kelasFilter').value],
    ['eskul_id', $('eskulFilter').value],
    ['status', $('statusFilter').value],
  ].forEach(([key, value]) => value && query.set(key, value));
  if (includePage) {
    query.set('page', page);
    query.set('page_size', pageSize);
  }
  return query;
}

function eskulOptions(selected, blank = 'Belum memilih', kelas = '') {
  const match = kelas.match(/\d+/);
  const grade = match && Number(match[0]) >= 1 && Number(match[0]) <= 6 ? Number(match[0]) : null;
  return `<option value="">${blank}</option>` + options.eskul.filter(eskul => Number(selected) === eskul.id || (grade && grade >= eskul.minimal_kelas)).map(eskul => `
    <option value="${eskul.id}" ${Number(selected) === eskul.id ? 'selected' : ''}>${esc(eskul.nama_eskul)}${eskul.minimal_kelas > 1 ? ` (Kelas ${eskul.minimal_kelas}+)` : ''}</option>
  `).join('');
}

async function loadStudents() {
  $('studentRows').innerHTML = '<tr><td colspan="8">Memuat data...</td></tr>';
  try {
    const data = await api('/api/students/manage?' + params());
    pages = data.pages;
    options = data.options;
    $('totalSiswa').textContent = data.summary.total;
    $('sudahDaftar').textContent = data.summary.assigned;
    $('belumDaftar').textContent = data.summary.unassigned;
    $('totalKelas').textContent = data.summary.classes;
    $('kelasFilter').innerHTML = '<option value="">Semua kelas</option>' + options.kelas.map(kelas => `
      <option ${kelas === $('kelasFilter').dataset.value ? 'selected' : ''}>${esc(kelas)}</option>
    `).join('');
    $('eskulFilter').innerHTML = '<option value="">Semua eskul</option>' + options.eskul.map(eskul => `
      <option value="${eskul.id}" ${String(eskul.id) === $('eskulFilter').dataset.value ? 'selected' : ''}>${esc(eskul.nama_eskul)}</option>
    `).join('');
    $('newEskul').innerHTML = eskulOptions(null, 'Belum memilih', $('newKelas').value);
    $('studentRows').innerHTML = data.items.map(student => `
      <tr>
        <td data-label="Pilih"><input class="student-check" type="checkbox" value="${student.id}" aria-label="Pilih ${esc(student.nama)}"></td>
        <td data-label="NIS"><input class="form-control form-control-sm" id="nis-${student.id}" value="${esc(student.nis)}" aria-label="NIS ${esc(student.nama)}"></td>
        <td data-label="NISN"><input class="form-control form-control-sm" id="nisn-${student.id}" value="${esc(student.nisn)}" aria-label="NISN ${esc(student.nama)}"></td>
        <td data-label="Nama"><input class="form-control form-control-sm" id="nama-${student.id}" value="${esc(student.nama)}" aria-label="Nama"></td>
        <td data-label="JK"><select class="form-select form-select-sm" id="jk-${student.id}" aria-label="Jenis kelamin"><option ${student.jeniskelamin === 'L' ? 'selected' : ''}>L</option><option ${student.jeniskelamin === 'P' ? 'selected' : ''}>P</option><option value="-" ${student.jeniskelamin === '-' ? 'selected' : ''}>Tidak diketahui</option></select></td>
        <td data-label="Kelas"><input class="form-control form-control-sm" id="kelas-${student.id}" value="${esc(student.kelas)}" aria-label="Kelas"></td>
        <td data-label="Eskul"><select class="form-select form-select-sm" id="eskul-${student.id}" aria-label="Eskul">${eskulOptions(student.eskul, 'Belum memilih', student.kelas)}</select></td>
        <td data-label="Aksi"><button class="btn btn-sm btn-primary" type="button" data-action="update-student" data-id="${student.id}">Simpan</button> <button class="btn btn-sm btn-outline-danger" type="button" data-action="delete-student" data-id="${student.id}">Hapus</button></td>
      </tr>
    `).join('') || '<tr><td colspan="8">Tidak ada data.</td></tr>';
    const nearby = new Set([1, pages, page - 2, page - 1, page, page + 1, page + 2].filter(number => number >= 1 && number <= pages));
    const numbers = [...nearby].sort((a, b) => a - b);
    const items = [];
    items.push(`<li class="page-item ${page === 1 ? 'disabled' : ''}"><button class="page-link" type="button" data-action="go-page" data-page="1" aria-label="Halaman pertama" ${page === 1 ? 'disabled' : ''}>«</button></li>`);
    items.push(`<li class="page-item ${page === 1 ? 'disabled' : ''}"><button class="page-link" type="button" data-action="go-page" data-page="${page - 1}" aria-label="Halaman sebelumnya" ${page === 1 ? 'disabled' : ''}>‹</button></li>`);
    numbers.forEach((number, index) => {
      if (index && number - numbers[index - 1] > 1) items.push('<li class="page-item disabled"><span class="page-link" aria-hidden="true">…</span></li>');
      items.push(`<li class="page-item ${number === page ? 'active' : ''}"><button class="page-link" type="button" data-action="go-page" data-page="${number}" aria-label="Halaman ${number}" ${number === page ? 'aria-current="page"' : ''}>${number}</button></li>`);
    });
    items.push(`<li class="page-item ${page === pages ? 'disabled' : ''}"><button class="page-link" type="button" data-action="go-page" data-page="${page + 1}" aria-label="Halaman berikutnya" ${page === pages ? 'disabled' : ''}>›</button></li>`);
    items.push(`<li class="page-item ${page === pages ? 'disabled' : ''}"><button class="page-link" type="button" data-action="go-page" data-page="${pages}" aria-label="Halaman terakhir" ${page === pages ? 'disabled' : ''}>»</button></li>`);
    $('pagination').innerHTML = items.join('');
    $('exportBtn').href = '/api/registrations/export?' + params(false);
    $('checkAll').checked = false;
  } catch (error) {
    $('studentRows').innerHTML = '<tr><td colspan="8">Data gagal dimuat.</td></tr>';
    Swal.fire('Gagal', error.message, 'error');
  }
}

function studentData(id) {
  const form = new FormData();
  ['nis', 'nisn', 'nama', 'jk', 'kelas'].forEach(key => {
    form.append(key === 'jk' ? 'jeniskelamin' : key, $(`${key}-${id}`).value.trim());
  });
  form.append('eskul_id', $(`eskul-${id}`).value);
  return form;
}

async function updateStudent(id) {
  try {
    await api(`/api/students/${id}/update`, { method: 'POST', body: studentData(id) });
    await Swal.fire('Tersimpan', 'Data siswa diperbarui', 'success');
    loadStudents();
  } catch (error) {
    Swal.fire('Gagal', error.message, 'error');
  }
}

async function createStudent() {
  const form = new FormData();
  [['nis', 'newNis'], ['nisn', 'newNisn'], ['nama', 'newNama'], ['jeniskelamin', 'newJk'], ['kelas', 'newKelas'], ['eskul_id', 'newEskul']].forEach(([key, id]) => {
    form.append(key, $(id).value.trim());
  });
  try {
    await api('/api/students/create', { method: 'POST', body: form });
    await Swal.fire('Ditambahkan', 'Siswa berhasil ditambah', 'success');
    loadStudents();
  } catch (error) {
    Swal.fire('Gagal', error.message, 'error');
  }
}

async function deleteStudent(id) {
  const name = $(`nama-${id}`).value;
  const result = await Swal.fire({
    title: `Hapus ${name}?`,
    text: 'Data siswa akan dihapus permanen.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Hapus',
    showLoaderOnConfirm: true,
    preConfirm: () => api(`/api/students/${id}`, { method: 'DELETE' }).catch(error => Swal.showValidationMessage(error.message)),
  });
  if (result.isConfirmed) loadStudents();
}

async function bulkDeleteStudents() {
  const ids = [...document.querySelectorAll('.student-check:checked')].map(input => Number(input.value));
  if (!ids.length) return Swal.fire('Pilih siswa', '', 'info');
  const result = await Swal.fire({
    title: `Hapus ${ids.length} siswa?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Hapus',
    showLoaderOnConfirm: true,
    preConfirm: () => api('/api/students/bulk-delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ids),
    }).catch(error => Swal.showValidationMessage(error.message)),
  });
  if (result.isConfirmed) loadStudents();
}

async function loadEskulManager() {
  $('eskulManager').textContent = 'Memuat data...';
  try {
    const data = await api('/api/eskul/manage');
    $('eskulManager').innerHTML = `
      <table class="table">
        <thead><tr><th>Nama</th><th>Minimum kelas</th><th>Siswa</th><th>Aksi</th></tr></thead>
        <tbody>${data.eskul.map(eskul => `
          <tr>
            <td data-label="Nama"><input class="form-control" id="manage-eskul-${eskul.id}" value="${esc(eskul.nama_eskul)}" aria-label="Nama eskul"></td>
            <td data-label="Minimum kelas"><select class="form-select" id="manage-minimal-${eskul.id}" aria-label="Minimum kelas">${[1,2,3,4,5,6].map(grade => `<option ${grade === eskul.minimal_kelas ? 'selected' : ''}>${grade}</option>`).join('')}</select></td>
            <td data-label="Siswa">${eskul.siswa_count}</td>
            <td data-label="Aksi"><button class="btn btn-sm btn-primary" type="button" data-action="save-eskul" data-id="${eskul.id}">Simpan</button> <button class="btn btn-sm btn-outline-danger" type="button" data-action="delete-eskul" data-id="${eskul.id}" data-count="${eskul.siswa_count}">Hapus</button></td>
          </tr>
        `).join('')}</tbody>
      </table>
    `;
  } catch (error) {
    $('eskulManager').textContent = 'Data gagal dimuat.';
    Swal.fire('Gagal', error.message, 'error');
  }
}

async function eskulRequest(url, name, minimalKelas) {
  const form = new FormData();
  form.append('nama_eskul', name);
  form.append('minimal_kelas', minimalKelas);
  return api(url, { method: 'POST', body: form });
}

async function createEskul() {
  try {
    await eskulRequest('/api/eskul/create', $('newEskulName').value.trim(), $('newEskulMinimum').value);
    $('newEskulName').value = '';
    await Swal.fire('Ditambahkan', 'Eskul baru tersedia', 'success');
    loadEskulManager();
    loadStudents();
  } catch (error) {
    Swal.fire('Gagal', error.message, 'error');
  }
}

async function saveEskul(id) {
  try {
    const data = await eskulRequest(`/api/eskul/${id}/update`, $(`manage-eskul-${id}`).value.trim(), $(`manage-minimal-${id}`).value);
    await Swal.fire('Tersimpan', `${data.affected_students} pilihan siswa dikosongkan.`, 'success');
    loadEskulManager();
    loadStudents();
  } catch (error) {
    Swal.fire('Gagal', error.message, 'error');
  }
}

async function deleteEskul(id, count) {
  const name = $(`manage-eskul-${id}`).value;
  const result = await Swal.fire({
    title: `Hapus ${name}?`,
    text: `Pilihan ${count} siswa akan dikosongkan.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Hapus',
    showLoaderOnConfirm: true,
    preConfirm: () => api(`/api/eskul/${id}`, { method: 'DELETE' }).catch(error => Swal.showValidationMessage(error.message)),
  });
  if (result.isConfirmed) {
    await Swal.fire('Dihapus', `${result.value.affected_students} pilihan siswa dikosongkan.`, 'success');
    loadEskulManager();
    loadStudents();
  }
}

async function previewStudentImport() {
  const file = $('studentImportFile').files[0];
  if (!file) return Swal.fire('Pilih file .xlsx', '', 'info');
  const form = new FormData();
  form.append('file', file);
  try {
    const data = await api('/api/students/preview-import', { method: 'POST', body: form });
    $('importStudentsBtn').disabled = !data.new_count;
    const sheets = data.sheet_summaries.map(sheet => `${sheet.sheet}: ${sheet.rows}`).join(', ');
    const skipped = data.skipped_rows.map(row => `${row.sheet} baris ${row.row}: ${row.reason}`).join('; ');
    $('importPreview').textContent = `${data.total} valid, ${data.new_count} baru, ${data.duplicate_database_count} duplikat database, ${data.duplicate_file_count} duplikat file. Sheet: ${sheets}.${skipped ? ` Dilewati: ${skipped}.` : ''}`;
  } catch (error) {
    Swal.fire('Gagal', error.message, 'error');
  }
}

async function importStudents() {
  const button = $('importStudentsBtn');
  const form = new FormData();
  form.append('file', $('studentImportFile').files[0]);
  button.disabled = true;
  try {
    const data = await api('/api/students/import', { method: 'POST', body: form });
    await Swal.fire('Import selesai', `${data.inserted} masuk, ${data.skipped} dilewati`, 'success');
    loadStudents();
  } catch (error) {
    button.disabled = false;
    Swal.fire('Gagal', error.message, 'error');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  $('newKelas').addEventListener('input', () => { $('newEskul').innerHTML = eskulOptions(null, 'Belum memilih', $('newKelas').value); });
  $('studentRows').addEventListener('input', event => {
    if (!event.target.id.startsWith('kelas-')) return;
    const id = event.target.id.slice(6);
    const select = $(`eskul-${id}`);
    select.innerHTML = eskulOptions(select.value, 'Belum memilih', event.target.value);
  });
  $('filters').addEventListener('submit', event => {
    event.preventDefault();
    $('kelasFilter').dataset.value = $('kelasFilter').value;
    $('eskulFilter').dataset.value = $('eskulFilter').value;
    page = 1;
    loadStudents();
  });
  $('pageSize').addEventListener('change', event => {
    pageSize = Number(event.target.value);
    page = 1;
    loadStudents();
  });
  $('checkAll').addEventListener('change', event => {
    document.querySelectorAll('.student-check').forEach(input => { input.checked = event.target.checked; });
  });
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-action]');
    if (!button) return;
    const id = Number(button.dataset.id);
    const actions = {
      'create-student': () => createStudent(),
      'bulk-delete-students': () => bulkDeleteStudents(),
      'preview-import': () => previewStudentImport(),
      'import-students': () => importStudents(),
      'create-eskul': () => createEskul(),
      'update-student': () => updateStudent(id),
      'delete-student': () => deleteStudent(id),
      'save-eskul': () => saveEskul(id),
      'delete-eskul': () => deleteEskul(id, Number(button.dataset.count)),
      'go-page': () => { page = Number(button.dataset.page); loadStudents(); },
    };
    actions[button.dataset.action]?.();
  });
  loadStudents();
  loadEskulManager();
});
