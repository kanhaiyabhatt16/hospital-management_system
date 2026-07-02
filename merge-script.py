import os
# Define the new first part of script.js
first_part = """// Base URL for your Flask API
const API_BASE_URL = '/api';
const MOBILE_BREAKPOINT = 992;
// Global variables for pagination and cached data
let currentPage = {
    patients: 1,
    doctors: 1,
    appointments: 1,
    bills: 1,
    medicalRecords: 1,
    departments: 1,
    staff: 1,
    insuranceProviders: 1,
    testTypes: 1,
    patientTests: 1,
    inventoryItems: 1
};
const itemsPerPage = 10;
// Cached data from backend (to avoid excessive API calls for dropdowns/charts)
let cachedPatients = [];
let cachedDoctors = [];
let cachedAppointments = [];
let cachedBills = [];
let cachedMedicalRecords = [];
let cachedDepartments = [];
let cachedStaff = [];
let cachedInsuranceProviders = [];
let cachedTestTypes = [];
let cachedPatientTests = [];
let cachedInventoryItems = [];
// Chart instances for destruction and recreation
let currentDashboardCharts = {};
let currentPatientCharts = {};
let currentDoctorCharts = {};
let currentAppointmentCharts = {};
let currentBillingCharts = {};
let currentMedicalRecordCharts = {};
let currentReportCharts = {};
// DOM Elements (for common use)
const darkModeToggle = document.getElementById('darkModeToggle');
// Removed erroneous 'document' assignment here.
// document="C:\\\\Users\\\\DELL-IN\\\\Desktop\\\\Kanhaiya Bhatt\\\\KMS\\\\your_project_folder\\\\templates\\\\index.html" // REMOVED THIS LINE
darkModeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
  // Re-render charts on dark mode change to update colors
  updateChartsOnThemeChange();
});
const hideMenuBtn = document.getElementById('hideMenuBtn');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileMenuIcon = document.getElementById('mobileMenuIcon');
const mobileCloseBtn = document.getElementById('mobileCloseBtn');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const hospitalNameModal = document.getElementById('hospitalNameModal');
const allSections = document.querySelectorAll('.management-section');
const dashboardSection = document.getElementById('dashboard-section');
// --- Mobile Navigation ---
function isMobileView() {
    return window.innerWidth <= MOBILE_BREAKPOINT;
}
function openMobileSidebar() {
    if (!isMobileView()) return;
    sidebar.classList.add('mobile-open');
    sidebarOverlay.classList.add('active');
    sidebarOverlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('sidebar-open');
    if (mobileMenuBtn) {
        mobileMenuBtn.setAttribute('aria-expanded', 'true');
        mobileMenuBtn.setAttribute('aria-label', 'Close navigation menu');
    }
    if (mobileMenuIcon) {
        mobileMenuIcon.classList.remove('fa-bars');
        mobileMenuIcon.classList.add('fa-times');
    }
}
function closeMobileSidebar() {
    sidebar.classList.remove('mobile-open');
    sidebarOverlay.classList.remove('active');
    sidebarOverlay.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('sidebar-open');
    if (mobileMenuBtn) {
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
        mobileMenuBtn.setAttribute('aria-label', 'Open navigation menu');
    }
    if (mobileMenuIcon) {
        mobileMenuIcon.classList.remove('fa-times');
        mobileMenuIcon.classList.add('fa-bars');
    }
}
function toggleMobileSidebar() {
    if (sidebar.classList.contains('mobile-open')) {
        closeMobileSidebar();
    } else {
        openMobileSidebar();
    }
}
function handleViewportChange() {
    if (!isMobileView()) {
        closeMobileSidebar();
    } else {
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
    }
    resizeActiveCharts();
}
function resizeActiveCharts() {
    [
        currentDashboardCharts,
        currentPatientCharts,
        currentDoctorCharts,
        currentAppointmentCharts,
        currentBillingCharts,
        currentMedicalRecordCharts,
        currentReportCharts
    ].forEach(chartCache => {
        Object.values(chartCache).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    });
}
// --- Utility Functions ---
/**
 * Fetches data from the API.
 * @param {string} endpoint - The API endpoint.
 * @returns {Promise<Array|Object>} - The JSON response data.
 */
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        alert(`Error fetching data: ${error.message}`);
        return null;
    }
}
/**
 * Sends data to the API (POST, PUT, DELETE).
 * @param {string} endpoint - The API endpoint.
 * @param {string} method - HTTP method (POST, PUT, DELETE).
 * @param {Object} data - The data to send (for POST/PUT).
 * @returns {Promise<Object>} - The JSON response data.
 */
async function sendData(endpoint, method, data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: data ? JSON.stringify(data) : null,
        };
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Send data error:', error);
        alert(`Error: ${error.message}`);
        return null;
    }
}
/**
 * Paginates an array of data.
 * @param {Array} data - The array to paginate.
 * @param {number} page - The current page number.
 * @param {number} perPage - Items per page.
 * @returns {Array} - The paginated subset of data.
 */
function paginate(data, page, perPage) {
    const start = (page - 1) * perPage;
    const end = start + perPage;
    return data.slice(start, end);
}
/**
 * Renders pagination controls for a given table.
 * @param {string} elementId - The ID of the pagination container.
 * @param {number} totalItems - Total number of items.
 * @param {string} type - The type of data (e.g., 'patients', 'doctors').
 */
function renderPagination(elementId, totalItems, type) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pagination = document.getElementById(elementId);
    pagination.innerHTML = '';
    if (totalPages <= 1) return;
    const prevLi = document.createElement('li');
    prevLi.className = 'page-item';
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="changePage('${type}', ${currentPage[type] - 1})">&laquo;</a>`;
    prevLi.classList.toggle('disabled', currentPage[type] === 1);
    pagination.appendChild(prevLi);
    let startPage = Math.max(1, currentPage[type] - 2);
    let endPage = Math.min(totalPages, currentPage[type] + 2);
    if (endPage - startPage < 4) {
        if (startPage === 1) {
            endPage = Math.min(totalPages, startPage + 4);
        } else if (endPage === totalPages) {
            startPage = Math.max(1, totalPages - 4);
        }
    }
    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = 'page-item';
        li.innerHTML = `<a class="page-link ${currentPage[type] === i ? 'active' : ''}" href="#" onclick="changePage('${type}', ${i})">${i}</a>`;
        pagination.appendChild(li);
    }
    const nextLi = document.createElement('li');
    nextLi.className = 'page-item';
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="changePage('${type}', ${currentPage[type] + 1})">&raquo;</a>`;
    nextLi.classList.toggle('disabled', currentPage[type] === totalPages);
    pagination.appendChild(nextLi);
}
/**
 * Changes the current page for a specific data type and re-renders the table.
 * @param {string} type - The type of data.
 * @param {number} page - The page number to change to.
 */
async function changePage(type, page) {
    let data;
    switch (type) {
        case 'patients': data = cachedPatients; break;
        case 'doctors': data = cachedDoctors; break;
        case 'appointments': data = cachedAppointments; break;
        case 'bills': data = cachedBills; break;
        case 'medicalRecords': data = cachedMedicalRecords; break;
        case 'departments': data = cachedDepartments; break;
        case 'staff': data = cachedStaff; break;
        case 'insuranceProviders': data = cachedInsuranceProviders; break;
        case 'testTypes': data = cachedTestTypes; break;
        case 'patientTests': data = cachedPatientTests; break;
        case 'inventoryItems': data = cachedInventoryItems; break;
        default: return;
    }
    const totalPages = Math.ceil(data.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    currentPage[type] = page;
    switch (type) {
        case 'patients': renderPatientsTable(data); break;
        case 'doctors': renderDoctorsTable(data); break;
        case 'appointments': renderAppointmentsTable(data); break;
        case 'bills': renderBillsTable(data); break;
        case 'medicalRecords': renderMedicalRecordsTable(data); break;
        case 'departments': renderDepartmentsTable(data); break;
        case 'staff': renderStaffTable(data); break;
        case 'insuranceProviders': renderInsuranceProvidersTable(data); break;
        case 'testTypes': renderTestTypesTable(data); break;
        case 'patientTests': renderPatientTestsTable(data); break;
        case 'inventoryItems': renderInventoryTable(data); break;
    }
}
/**
 * Creates or updates a Chart.js chart.
 * @param {string} canvasId - The ID of the canvas element.
 * @param {string} type - The chart type (e.g., 'bar', 'pie', 'line').
 * @param {string} label - The label for the dataset.
 * @param {Array<string>} labels - Array of labels for the x-axis or segments.
 * @param {Array<number>} data - Array of data values.
 * @param {Object} chartCache - The global object to store chart instances (e.g., currentPatientCharts).
 */
function createChart(canvasId, type, label, labels, data, chartCache) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.warn(`Canvas element with ID '${canvasId}' not found.`);
        return;
    }
    const chartContext = ctx.getContext('2d');
    if (chartCache[canvasId] && typeof chartCache[canvasId].destroy === 'function') {
        chartCache[canvasId].destroy();
    }
    const backgroundColors = [
        'rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)', 'rgba(75, 192, 192, 0.7)',
        'rgba(255, 159, 64, 0.7)', 'rgba(153, 102, 255, 0.7)', 'rgba(255, 206, 86, 0.7)',
        'rgba(201, 203, 207, 0.7)', 'rgba(231, 76, 60, 0.7)', 'rgba(46, 204, 113, 0.7)',
        'rgba(147, 112, 219, 0.7)', 'rgba(255, 192, 203, 0.7)', 'rgba(0, 128, 128, 0.7)'
    ];
    const borderColors = backgroundColors.map(color => color.replace('0.7', '1'));
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#f5f5f5' : '#333';
    const gridColor = isDarkMode ? 'rgba(200, 200, 200, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const chartData = {
        labels: labels,
        datasets: [{
            label: label,
            data: data,
            backgroundColor: (type === 'pie' || type === 'doughnut') ?
                backgroundColors.slice(0, labels.length) :
                'rgba(54, 162, 235, 0.7)',
            borderColor: (type === 'pie' || type === 'doughnut') ?
                borderColors.slice(0, labels.length) :
                'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            fill: false,
            tension: 0.4
        }]
    };
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: (type === 'pie' || type === 'doughnut') ? 'bottom' : 'top',
                labels: {
                    color: textColor
                }
            },
            title: {
                display: true,
                text: label,
                color: textColor
            }
        },
        scales: {
            x: {
                ticks: { color: textColor },
                grid: { color: gridColor }
            },
            y: {
                ticks: { color: textColor },
                grid: { color: gridColor }
            }
        }
    };
    const newChart = new Chart(chartContext, {
        type: type,
        data: chartData,
        options: chartOptions
    });
    chartCache[canvasId] = newChart;
}
/**
 * Formats a date string to a more readable format.
 * @param {string} dateStr - The date string (e.g., 'YYYY-MM-DD').
 * @returns {string} - Formatted date.
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}
/**
 * Formats a time string to a more readable format.
 * @param {string} timeStr - The time string (e.g., 'HH:MM:SS').
 * @returns {string} - Formatted time.
 */
function formatTime(timeStr) {
    if (!timeStr) return '';
    const [hours, minutes] = timeStr.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
}
/**
 * Truncates text to a specified maximum length and adds '...' if longer.
 * @param {string} text - The text to truncate.
 * @param {number} maxLength - The maximum length.
 * @returns {string} - Truncated text.
 */
function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}
/**
 * Returns a CSS class based on the status for styling badges.
 * @param {string} status - The status string.
 * @returns {string} - The corresponding CSS class name.
 */
function getStatusClass(status) {
    if (!status) return '';
    return status.toLowerCase().replace(/ /g, '-');
}
/**
 * Renders search results in a table.
 * @param {string} tableBodyId - ID of the table body element.
 * @param {Array<Object>} results - Array of search results.
 * @param {string} type - Type of data (e.g., 'patient', 'doctor').
 */
function renderSearchResults(tableBodyId, results, type) {
    const tableBody = document.getElementById(tableBodyId);
    tableBody.innerHTML = '';
    const noResultsMessage = document.getElementById(`no${type.charAt(0).toUpperCase() + type.slice(1)}SearchResults`);
    const resultsContainer = document.getElementById(`search${type.charAt(0).toUpperCase() + type.slice(1)}Results`);
    if (results.length === 0) {
        noResultsMessage.style.display = 'block';
        resultsContainer.style.display = 'block';
    } else {
        noResultsMessage.style.display = 'none';
        results.forEach(item => {
            const row = document.createElement('tr');
            let innerHTML = ''; // Initialize as empty string
            if (type === 'patient') {
                innerHTML = `
                    <td>${item.patient_id}</td>
                    <td>${item.name}</td>
                    <td>${item.age}</td>
                    <td>${item.gender}</td>
                    <td>${item.phone || ''}</td>
                    <td>${item.blood_type || ''}</td>
                    <td>
                        <button class="btn btn-primary" onclick="viewPatientDetails(${item.patient_id})"><i class="fas fa-eye"></i> View</button>
                    </td>
                `;
            } else if (type === 'doctor') {
                innerHTML = `
                    <td>${item.doctor_id}</td>
                    <td>${item.name}</td>
                    <td>${item.specialization}</td>
                    <td>${item.department_name || ''}</td>
                    <td>$${item.consultation_fee.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-primary" onclick="viewDoctorDetails(${item.doctor_id})"><i class="fas fa-eye"></i> View</button>
                    </td>
                `;
            } else if (type === 'appointment') {
                innerHTML = `
                    <td>${item.appointment_id}</td>
                    <td>${item.patient_name}</td>
                    <td>${item.doctor_name}</td>
                    <td>${formatDate(item.date)}</td>
                    <td>${formatTime(item.time)}</td>
                    <td><span class="status-badge status-${getStatusClass(item.status)}">${item.status}</span></td>
                    <td>
                        <button class="btn btn-primary" onclick="viewAppointmentDetails(${item.appointment_id})"><i class="fas fa-eye"></i> View</button>
                    </td>
                `;
            } else if (type === 'bill') {
                innerHTML = `
                    <td>${item.invoice_number}</td>
                    <td>${item.patient_name}</td>
                    <td>${formatDate(item.date)}</td>
                    <td>$${item.amount.toFixed(2)}</td>
                    <td><span class="status-badge status-${getStatusClass(item.status)}">${item.status}</span></td>
                    <td>
                        <button class="btn btn-primary" onclick="viewBillDetails(${item.bill_id})"><i class="fas fa-eye"></i> View</button>
                    </td>
                `;
            } else if (type === 'medicalRecord') {
                innerHTML = `
                    <td>${item.record_id}</td>
                    <td>${item.patient_name}</td>
                    <td>${item.doctor_name || 'N/A'}</td>
                    <td>${truncateText(item.diagnosis, 30)}</td>
                    <td>${formatDate(item.date)}</td>
                    <td>
                        <button class="btn btn-primary" onclick="viewMedicalRecordDetails(${item.record_id})"><i class="fas fa-eye"></i> View</button>
                    </td>
                `;
            }
            row.innerHTML = innerHTML;
            tableBody.appendChild(row);
        });
        resultsContainer.style.display = 'block';
    }
}
// --- Common UI/Navigation Logic ---
document.addEventListener('DOMContentLoaded', async function () {
    // Initial data load for dropdowns etc.
    await preloadAllData();
    // Set hospital name
    if (!localStorage.getItem('hospitalName')) {
        if (hospitalNameModal) {
            hospitalNameModal.style.display = 'block';
        }
    } else {
        const hospitalNameEl = document.getElementById('hospitalName');
        if (hospitalNameEl) {
            hospitalNameEl.textContent = localStorage.getItem('hospitalName');
        }
    }
    // Dark mode toggle
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }
    // Show dashboard by default
    showDashboard();
    // Event listener for medical record follow-up checkbox
    const medicalRecordFollowUpRequired = document.getElementById('medicalRecordFollowUpRequired');
    const medicalRecordFollowUpDateGroup = document.getElementById('medicalRecordFollowUpDateGroup');
    if (medicalRecordFollowUpRequired) {
        medicalRecordFollowUpRequired.addEventListener('change', function() {
            if (this.checked) {
                medicalRecordFollowUpDateGroup.style.display = 'block';
            } else {
                medicalRecordFollowUpDateGroup.style.display = 'none';
                document.getElementById('medicalRecordFollowUpDate').value = '';
            }
        });
    }
    const updateMedicalRecordFollowUpRequired = document.getElementById('updateMedicalRecordFollowUpRequired');
    const updateMedicalRecordFollowUpDateGroup = document.getElementById('updateMedicalRecordFollowUpDateGroup');
    if (updateMedicalRecordFollowUpRequired) {
        updateMedicalRecordFollowUpRequired.addEventListener('change', function() {
            if (this.checked) {
                updateMedicalRecordFollowUpDateGroup.style.display = 'block';
            } else {
                updateMedicalRecordFollowUpDateGroup.style.display = 'none';
                document.getElementById('updateMedicalRecordFollowUpDate').value = '';
            }
        });
    }
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileSidebar);
    }
    if (mobileCloseBtn) {
        mobileCloseBtn.addEventListener('click', closeMobileSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeMobileSidebar);
    }
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
            closeMobileSidebar();
        }
    });
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleViewportChange, 150);
    });
    handleViewportChange();
});
hideMenuBtn.addEventListener('click', function () {
    if (isMobileView()) return;
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
    resizeActiveCharts();
});
darkModeToggle.addEventListener('change', function () {
    if (this.checked) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'enabled');
    } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
    }
    // Update all charts colors on mode change
    updateChartsOnThemeChange();
});
function updateChartsOnThemeChange() {
    // Destroy all existing charts and clear cache objects
    Object.values(currentDashboardCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentDashboardCharts = {};
    Object.values(currentPatientCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentPatientCharts = {};
    Object.values(currentDoctorCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentDoctorCharts = {};
    Object.values(currentAppointmentCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentAppointmentCharts = {};
    Object.values(currentBillingCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentBillingCharts = {};
    Object.values(currentMedicalRecordCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentMedicalRecordCharts = {};
    Object.values(currentReportCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentReportCharts = {};
    // Re-render current active charts
    const activeSection = document.querySelector('.management-section.active');
    if (activeSection) {
        const sectionId = activeSection.id;
        if (sectionId === 'dashboard-section') {
            updateDashboardCharts();
        } else if (sectionId === 'patient-management') {
            renderPatientCharts(cachedPatients);
        } else if (sectionId === 'doctor-management') {
            renderDoctorCharts(cachedDoctors);
        } else if (sectionId === 'appointment-management') {
            renderAppointmentCharts(cachedAppointments);
        } else if (sectionId === 'billing-management') {
            renderBillingCharts(cachedBills);
        } else if (sectionId === 'medical-records') {
            renderMedicalRecordCharts(cachedMedicalRecords);
        } else if (sectionId === 'reports-analytics') {
            // Re-render specific report if active
            const activeReport = document.querySelector('#reports-analytics .card:not(.hidden-section)');
            if (activeReport) {
                const reportId = activeReport.id;
                if (reportId === 'financial-reports') renderFinancialReports();
                if (reportId === 'operational-reports') renderOperationalReports();
                if (reportId === 'doctor-performance-reports') renderDoctorPerformanceReports();
                if (reportId === 'patient-statistics-reports') renderPatientStatisticsReports();
            }
        }
    }
}
function saveHospitalName() {
    const name = document.getElementById('hospitalNameInput').value;
    if (name) {
        localStorage.setItem('hospitalName', name);
        document.getElementById('hospitalName').textContent = name;
        closeHospitalNameModal();
    }
}
function closeHospitalNameModal() {
    hospitalNameModal.style.display = 'none';
}
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}
function hideAllSections() {
    allSections.forEach(section => {
        section.classList.remove('active');
    });
}
function updateNavActive(activeId) {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick')?.includes(activeId)) {
            link.classList.add('active');
        }
    });
}
function logout() {
    if (confirm('Are you sure you want to exit?')) {
        closeMobileSidebar();
        alert('Exiting Hospital Management System. Goodbye!');
        // In a real web app, you might clear session data or redirect to a login page.
        // window.close() might not work in all modern browsers due to security policies.
    }
}
/**
 * Hides all forms/lists within a specific management section.
 * @param {string} sectionId - The ID of the management section (e.g., 'patient-management').
 */
function hideAllSubSections(sectionId) {
    document.querySelectorAll(`#${sectionId} .card.hidden-section`).forEach(el => el.style.display = 'none');
    document.querySelector(`#${sectionId} .visualization-container`)?.classList.add('hidden-section');
    document.querySelector(`#${sectionId} .table-responsive`)?.parentElement?.classList.add('hidden-section'); // Hides lists
}
// --- Preload Data Function ---
async function preloadAllData() {
    cachedPatients = await fetchData('patients') || [];
    cachedDoctors = await fetchData('doctors') || [];
    cachedAppointments = await fetchData('appointments') || [];
    cachedDepartments = await fetchData('departments') || [];
    cachedBills = await fetchData('bills') || [];
    cachedMedicalRecords = await fetchData('records') || [];
    cachedStaff = await fetchData('staff') || [];
    cachedInsuranceProviders = await fetchData('insurance') || [];
    cachedTestTypes = await fetchData('tests/types') || [];
    cachedPatientTests = await fetchData('tests/patients') || [];
    cachedInventoryItems = await fetchData('inventory') || [];
    // Populate dropdowns once data is loaded
    populatePatientDropdown('appointmentPatient');
    populatePatientDropdown('updateAppointmentPatient');
    populatePatientDropdown('billPatient');
    populatePatientDropdown('medicalRecordPatient');
    populatePatientDropdown('patientTestPatient');
    populateDoctorDropdown('appointmentDoctor');
    populateDoctorDropdown('updateAppointmentDoctor');
    populateDoctorDropdown('medicalRecordDoctor');
    populateDoctorDropdown('patientTestDoctor');
    populateDepartmentDropdown('doctorDepartment');
    populateDepartmentDropdown('updateDoctorDepartment');
    populateDepartmentDropdown('staffDepartment');
    populateDepartmentDropdown('updateStaffDepartment');
    populateAppointmentDropdown('billAppointment');
    populateTestTypeDropdown('patientTestType');
}
// --- DASHBOARD FUNCTIONS ---
async function showDashboard() {
    hideAllSections();
    dashboardSection.classList.add('active');
    updateNavActive('dashboard');
    closeMobileSidebar();
    await updateDashboardMetrics();
    updateDashboardCharts();
}
async function updateDashboardMetrics() {
    const patients = await fetchData('patients');
    const doctors = await fetchData('doctors');
    const todayAppointments = await fetchData('reports/today-appointments');
    const pendingBills = await fetchData('bills'); // Fetch all to filter client-side
    document.getElementById('totalPatients').textContent = patients ? patients.length : 0;
    document.getElementById('totalDoctors').textContent = doctors ? doctors.length : 0;
    document.getElementById('todaysAppointments').textContent = todayAppointments ? todayAppointments.length : 0;
    document.getElementById('pendingBills').textContent = pendingBills ? pendingBills.filter(bill => bill.status === 'Unpaid' || bill.status === 'Overdue').length : 0;
}
async function updateDashboardCharts() {
    // Clear existing dashboard charts
    Object.values(currentDashboardCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentDashboardCharts = {};
    // Appointments Trend (Daily)
    const appointmentsData = await fetchData('appointments');
    if (appointmentsData) {
        const dailyAppointments = {};
        const today = new Date();
        for (let i = 6; i >= 0; i--) { // Last 7 days
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            dailyAppointments[dateStr] = 0;
        }
        appointmentsData.forEach(app => {
            const appDate = app.date.split('T')[0]; // Ensure date format matches
            if (dailyAppointments.hasOwnProperty(appDate)) {
                dailyAppointments[appDate]++;
            }
        });
        const labels = Object.keys(dailyAppointments).map(d => new Date(d).toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }));
        const data = Object.values(dailyAppointments);
        createChart('appointmentsChart', 'line', 'Appointments Trend (Last 7 Days)', labels, data, currentDashboardCharts);
    }
    // Revenue Trend (Daily)
    const billsData = await fetchData('bills');
    if (billsData) {
        const dailyRevenue = {};
        const today = new Date();
        for (let i = 6; i >= 0; i--) { // Last 7 days
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            dailyRevenue[dateStr] = 0;
        }
        billsData.filter(bill => bill.status === 'Paid').forEach(bill => {
            const billDate = bill.date.split('T')[0];
            if (dailyRevenue.hasOwnProperty(billDate)) {
                dailyRevenue[billDate] += parseFloat(bill.amount);
            }
        });
        const labels = Object.keys(dailyRevenue).map(d => new Date(d).toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }));
        const data = Object.values(dailyRevenue);
        createChart('revenueChart', 'line', 'Revenue Trend (Last 7 Days)', labels, data, currentDashboardCharts);
    }
}
async function changeDashboardTimePeriod(type, period) {
    const selectorId = type === 'appointments' ? 'appointmentsTimeSelector' : 'revenueTimeSelector';
    document.getElementById(selectorId).querySelectorAll('button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(period)) {
            btn.classList.add('active');
        }
    });
    if (type === 'appointments') {
        const appointmentsData = await fetchData('appointments');
        if (appointmentsData) {
            let aggregatedData = {};
            const now = new Date();
            if (period === 'daily') {
                for (let i = 6; i >= 0; i--) { // Last 7 days
                    const date = new Date(now);
                    date.setDate(now.getDate() - i);
                    aggregatedData[date.toISOString().split('T')[0]] = 0;
                }
                appointmentsData.forEach(app => {
                    const appDate = app.date.split('T')[0];
                    if (aggregatedData.hasOwnProperty(appDate)) {
                        aggregatedData[appDate]++;
                    }
                });
                const labels = Object.keys(aggregatedData).map(d => new Date(d).toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }));
                const data = Object.values(aggregatedData);
                createChart('appointmentsChart', 'line', 'Appointments Trend (Daily)', labels, data, currentDashboardCharts);
            } else if (period === 'weekly') {
                // For simplicity, generate random data for weekly/monthly for now
                // In a real app, you'd aggregate database data by week/month
                const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
                const data = labels.map(() => Math.floor(Math.random() * 100) + 50);
                createChart('appointmentsChart', 'bar', 'Appointments Trend (Weekly)', labels, data, currentDashboardCharts);
            } else if (period === 'monthly') {
                const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']; // Example months
                const data = labels.map(() => Math.floor(Math.random() * 300) + 100);
                createChart('appointmentsChart', 'bar', 'Appointments Trend (Monthly)', labels, data, currentDashboardCharts);
            }
        }
    } else { // Revenue
        const billsData = await fetchData('bills');
        if (billsData) {
            let aggregatedData = {};
            const now = new Date();
            if (period === 'daily') {
                for (let i = 6; i >= 0; i--) { // Last 7 days
                    const date = new Date(now);
                    date.setDate(now.getDate() - i);
                    aggregatedData[date.toISOString().split('T')[0]] = 0;
                }
                billsData.filter(bill => bill.status === 'Paid').forEach(bill => {
                    const billDate = bill.date.split('T')[0];
                    if (aggregatedData.hasOwnProperty(billDate)) {
                        aggregatedData[billDate] += parseFloat(bill.amount);
                    }
                });
                const labels = Object.keys(aggregatedData).map(d => new Date(d).toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }));
                const data = Object.values(aggregatedData);
                createChart('revenueChart', 'line', 'Revenue Trend (Daily)', labels, data, currentDashboardCharts);
            } else if (period === 'weekly') {
                const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
                const data = labels.map(() => Math.floor(Math.random() * 5000) + 2000);
                createChart('revenueChart', 'bar', 'Revenue Trend (Weekly)', labels, data, currentDashboardCharts);
            } else if (period === 'monthly') {
                const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
                const data = labels.map(() => Math.floor(Math.random() * 10000) + 5000);
                createChart('revenueChart', 'bar', 'Revenue Trend (Monthly)', labels, data, currentDashboardCharts);
            }
        }
    }
}
// Function to handle showing management sections and updating nav links
function showSection(sectionId) {
    hideAllSections(); // Hide all management sections first
    hideAllSubSections(sectionId); // Hide all sub-sections within the target management section
    document.getElementById(sectionId).classList.add('active'); // Show the target management section
    // Update active state of navigation links
    updateNavActive(sectionId);
    closeMobileSidebar();
    // Specific actions for each section when shown
    if (sectionId === 'patient-management') {
        showAllPatients(); // Default to showing all patients when entering patient management
    } else if (sectionId === 'doctor-management') {
        showAllDoctors(); // Default to showing all doctors
    } else if (sectionId === 'appointment-management') {
        showAllAppointments(); // Default to showing all appointments
    } else if (sectionId === 'billing-management') {
        showAllBills(); // Default to showing all bills
    } else if (sectionId === 'medical-records') {
        showAllMedicalRecords(); // Default to showing all medical records
    } else if (sectionId === 'department-management') {
        showAllDepartments();
    } else if (sectionId === 'staff-management') {
        showAllStaff();
    } else if (sectionId === 'insurance-management') {
        showAllInsuranceProviders();
    } else if (sectionId === 'test-management') {
        showAllPatientTests(); // Default to patient tests
    } else if (sectionId === 'inventory-management') {
        showAllInventory();
    } else if (sectionId === 'reports-analytics') {
        showFinancialReports(); // Default to showing financial reports
    }
}
// --- PATIENT MANAGEMENT ---
function showPatientForm(type) {
    hideAllSubSections('patient-management');
    document.getElementById(`${type}-patient-form`).style.display = 'block';
    if (type === 'add') {
        document.getElementById('patientForm').reset();
    } else {
        document.getElementById('updatePatientForm').classList.add('hidden-section'); // Hide form until patient loaded
        document.getElementById('updatePatientId').value = ''; // Clear previous ID
    }
}
function hidePatientForm(type) {
    document.getElementById(`${type}-patient-form`).style.display = 'none';
}
function showAllPatients() {
    hideAllSubSections('patient-management');
    renderPatientsTable(cachedPatients);
    renderPatientCharts(cachedPatients);
    document.getElementById('patient-list').style.display = 'block';
    document.getElementById('patient-visualizations').classList.remove('hidden-section');
}
function showPatientSearch() {
    hideAllSubSections('patient-management');
    document.getElementById('search-patient-form').style.display = 'block';
    document.getElementById('searchPatientQuery').value = ''; // Clear previous query
    document.getElementById('searchPatientResults').classList.add('hidden-section'); // Hide results until search
}
function showPatientDelete() {
    hideAllSubSections('patient-management');
    document.getElementById('delete-patient-form').style.display = 'block';
    document.getElementById('deletePatientId').value = ''; // Clear previous ID
}
async function addPatient() {
    const patientData = {
        name: document.getElementById('patientName').value,
        age: parseInt(document.getElementById('patientAge').value),
        gender: document.getElementById('patientGender').value,
        phone: document.getElementById('patientPhone').value || null,
        email: document.getElementById('patientEmail').value || null,
        address: document.getElementById('patientAddress').value || null,
        blood_type: document.getElementById('patientBloodType').value || null,
        medical_history: document.getElementById('patientMedicalHistory').value || null,
        allergies: document.getElementById('patientAllergies').value || null,
        disease: null // Not collected in this form
    };
    const result = await sendData('patients', 'POST', patientData);
    if (result) {
        alert(result.message);
        document.getElementById('patientForm').reset();
        cachedPatients = await fetchData('patients') || []; // Refresh cache
        showAllPatients();
        await updateDashboardMetrics();
    }
}
async function loadPatientForUpdate() {
    const patientId = document.getElementById('updatePatientId').value;
    if (!patientId) {
        alert('Please enter a Patient ID.');
        return;
    }
    const patient = await fetchData(`patients/${patientId}`);
    if (patient) {
        document.getElementById('updatePatientName').value = patient.name;
        document.getElementById('updatePatientAge').value = patient.age;
        document.getElementById('updatePatientGender').value = patient.gender;
        document.getElementById('updatePatientPhone').value = patient.phone || '';
        document.getElementById('updatePatientEmail').value = patient.email || '';
        document.getElementById('updatePatientAddress').value = patient.address || '';
        document.getElementById('updatePatientBloodType').value = patient.blood_type || '';
        document.getElementById('updatePatientMedicalHistory').value = patient.medical_history || '';
        document.getElementById('updatePatientAllergies').value = patient.allergies || '';
        document.getElementById('updatePatientForm').classList.remove('hidden-section');
    } else {
        document.getElementById('updatePatientForm').classList.add('hidden-section');
        alert('Patient not found!');
    }
}
async function updatePatient() {
    const patientId = document.getElementById('updatePatientId').value;
    const patientData = {
        name: document.getElementById('updatePatientName').value,
        age: parseInt(document.getElementById('updatePatientAge').value),
        gender: document.getElementById('updatePatientGender').value,
        phone: document.getElementById('updatePatientPhone').value || null,
        email: document.getElementById('updatePatientEmail').value || null,
        address: document.getElementById('updatePatientAddress').value || null,
        blood_type: document.getElementById('updatePatientBloodType').value || null,
        medical_history: document.getElementById('updatePatientMedicalHistory').value || null,
        allergies: document.getElementById('updatePatientAllergies').value || null
    };
    const result = await sendData(`patients/${patientId}`, 'PUT', patientData);
    if (result) {
        alert(result.message);
        document.getElementById('updatePatientForm').reset();
        document.getElementById('updatePatientForm').classList.add('hidden-section');
        document.getElementById('updatePatientId').value = '';
        cachedPatients = await fetchData('patients') || []; // Refresh cache
        showAllPatients();
    }
}
async function confirmDeletePatient() {
    const patientId = document.getElementById('deletePatientId').value;
    if (!patientId) {
        alert('Please enter a Patient ID to delete.');
        return;
    }
    if (confirm(`Are you sure you want to delete patient with ID ${patientId}? This action cannot be undone.`)) {
        const result = await sendData(`patients/${patientId}`, 'DELETE');
        if (result) {
            alert(result.message);
            document.getElementById('deletePatientId').value = '';
            cachedPatients = await fetchData('patients') || []; // Refresh cache
            showAllPatients();
            await updateDashboardMetrics();
        }
    }
}
function renderPatientsTable(patients) {
    const tableBody = document.getElementById('patientsTableBody');
    tableBody.innerHTML = '';
    const paginatedPatients = paginate(patients, currentPage.patients, itemsPerPage);
    if (paginatedPatients.length === 0) {
        document.getElementById('noPatientsMessage').style.display = 'block';
    } else {
        document.getElementById('noPatientsMessage').style.display = 'none';
        paginatedPatients.forEach(patient => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${patient.patient_id}</td>
                <td>${patient.name}</td>
                <td>${patient.age}</td>
                <td>${patient.gender}</td>
                <td>${patient.phone || ''}</td>
                <td>${patient.blood_type || ''}</td>
                <td>
                    <button class="btn btn-primary" onclick="viewPatientDetails(${patient.patient_id})"><i class="fas fa-eye"></i> View</button>
                    <button class="btn btn-success" onclick="editPatient(${patient.patient_id})"><i class="fas fa-edit"></i> Edit</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }
    renderPagination('patientPagination', patients.length, 'patients');
}
function renderPatientCharts(patients) {
    // Destroy existing charts if any
    Object.values(currentPatientCharts).forEach(chart => { if (chart && typeof chart.destroy === 'function') chart.destroy(); });
    currentPatientCharts = {};
    if (patients.length === 0) {
        document.getElementById('patient-visualizations').classList.add('hidden-section');
        return;
    }
    document.getElementById('patient-visualizations').classList.remove('hidden-section'); // Ensure charts container is visible
    const genderCounts = patients.reduce((acc, p) => {
        acc[p.gender] = (acc[p.gender] || 0) + 1;
        return acc;
    }, {});
    createChart('patientGenderChart', 'pie', 'Patient Gender Distribution', Object.keys(genderCounts), Object.values(genderCounts), currentPatientCharts);
    const ageGroups = { '0-18': 0, '19-35': 0, '36-50': 0, '51+': 0 };
    patients.forEach(p => {
        if (p.age <= 18) ageGroups['0-18']++; else if (p.age <= 35) ageGroups['19-35']++; else if (p.age <= 50) ageGroups['36-50']++; else ageGroups['51+']++;
    });
    createChart('patientAgeDistributionChart', 'bar', 'Patient Age Distribution', Object.keys(ageGroups), Object.values(ageGroups), currentPatientCharts);
    const bloodTypeCounts = patients.reduce((acc, p) => {
        if (p.blood_type) {
            acc[p.blood_type] = (acc[p.blood_type] || 0) + 1;
        }
        return acc;
    }, {});
    createChart('patientBloodTypeChart', 'doughnut', 'Patient Blood Type', Object.keys(bloodTypeCounts), Object.values(bloodTypeCounts), currentPatientCharts);
    // Assuming 'created_at' for registration date, adjust if your schema uses a different column
    const registrationTrend = patients.reduce((acc, p) => {
        const date = p.registrationDate ? p.registrationDate.split(' ')[0] : 'Unknown'; // Extract date part from 'YYYY-MM-DD HH:MM:SS'
        if (date !== 'Unknown') {
            acc[date] = (acc[date] || 0) + 1;
        }
        return acc;
    }, {});
    const sortedDates = Object.keys(registrationTrend).sort();
    createChart('patientRegistrationTrendChart', 'line', 'Patient Registrations Over Time', sortedDates, sortedDates.map(d => registrationTrend[d]), currentPatientCharts);
}
async function viewPatientDetails(id) {
    const patient = await fetchData(`patients/${id}`);
    if (patient) {
        const content = `
            <p><strong>Name:</strong> ${patient.name}</p>
            <p><strong>Age:</strong> ${patient.age}</p>
            <p><strong>Gender:</strong> ${patient.gender}</p>
            <p><strong>Phone:</strong> ${patient.phone || 'N/A'}</p>
            <p><strong>Email:</strong> ${patient.email || 'N/A'}</p>
            <p><strong>Address:</strong> ${patient.address || 'N/A'}</p>
            <p><strong>Blood Type:</strong> ${patient.blood_type || 'N/A'}</p>
            <p><strong>Medical History:</strong> ${patient.medical_history || 'N/A'}</p>
            <p><strong>Allergies:</strong> ${patient.allergies || 'N/A'}</p>
            <p><strong>Disease:</strong> ${patient.disease || 'N/A'}</p>
            <p><strong>Insurance Provider ID:</strong> ${patient.insurance_provider_id || 'N/A'}</p>
            <p><strong>Policy Number:</strong> ${patient.insurance_policy_number || 'N/A'}</p>
            <p><strong>Primary Physician:</strong> ${patient.primary_physician || 'N/A'}</p>
            <p><strong>Emergency Contact:</strong> ${patient.emergency_contact || 'N/A'}</p>
            <p><strong>Emergency Phone:</strong> ${patient.emergency_phone || 'N/A'}</p>
        `;
        document.getElementById('patientDetailsContent').innerHTML = content;
        document.getElementById('patientDetailsModal').style.display = 'block';
    }
}
function editPatient(id) {
    closeModal('patientDetailsModal');
    showPatientForm('update');
    document.getElementById('updatePatientId').value = id;
    loadPatientForUpdate();
}
async function searchPatient() {
    const query = document.getElementById('searchPatientQuery').value.toLowerCase();
    const results = cachedPatients.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.patient_id.toString().includes(query) ||
        (p.phone && p.phone.includes(query)) ||
        (p.disease && p.disease.toLowerCase().includes(query))
    );
    renderSearchResults('searchPatientResultsBody', results, 'patient');
}
async function exportPatients() {
    // Direct link to the Flask API endpoint for CSV export
    window.open(`${API_BASE_URL}/patients/export/csv`, '_blank');
    alert('Exporting patient data as CSV. Please check your downloads.');
}
// --- DOCTOR MANAGEMENT ---
function showDoctorForm(type) {
    hideAllSubSections('doctor-management');
    document.getElementById(`${type}-doctor-form`).style.display = 'block';
    populateDepartmentDropdown(`${type === 'add' ? 'doctor' : 'updateDoctor'}Department`);
    if (type === 'add') {
        document.getElementById('doctorForm').reset();
    } else {
        document.getElementById('updateDoctorForm').classList.add('hidden-section');
        document.getElementById('updateDoctorId').value = '';
    }
}
function hideDoctorForm(type) {
    document.getElementById(`${type}-doctor-form`).style.display = 'none';
}
function showAllDoctors() {
    hideAllSubSections('doctor-management');
    renderDoctorsTable(cachedDoctors);
    renderDoctorCharts(cachedDoctors);
"""
# Read the original script.js file to get the remaining part
with open('static/script.js', 'r') as f:
    orig_content = f.read()
# Locate 'document.getElementById(\'doctor-list\').style.display = \'block\';'
target_str = "document.getElementById('doctor-list').style.display = 'block';"
start_idx = orig_content.find(target_str)
if start_idx == -1:
    print("Error: Could not locate start anchor in original script.js!")
    exit(1)
# Get the second part
second_part = orig_content[start_idx:]
# Combine them
full_new_content = first_part + second_part
# Write to static/script.js
with open('static/script.js', 'w') as f:
    f.write(full_new_content)
print("Merge completed successfully!")
