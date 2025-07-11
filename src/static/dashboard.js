// Global variables
let allData = [];
let filteredData = [];
let currentFilters = {
    year: '2024',
    month: '',
    sifat: '',
    status: '',
    lokasi: ''
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    setupEventListeners();
    updateDateTime();
    setInterval(updateDateTime, 1000);
});

// Load dashboard data from API
async function loadDashboardData() {
    try {
        // Show loading state
        showLoadingState();
        
        const response = await fetch('/api/dashboard/data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Loaded data:', data); // Debug log
        
        allData = data.data || [];
        filteredData = [...allData];
        
        // Hide loading state
        hideLoadingState();
        
        updateDashboard();
        populateLocationList();
        populateLokasiButtons();
        
        console.log('Dashboard updated with', allData.length, 'records');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        hideLoadingState();
        showErrorState(error.message);
    }
}

// Show loading state
function showLoadingState() {
    // Add loading indicators to KPI cards
    document.querySelectorAll('.kpi-value').forEach(el => {
        el.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    });
}

// Hide loading state
function hideLoadingState() {
    // Loading will be replaced by actual data
}

// Show error state
function showErrorState(message) {
    document.querySelectorAll('.kpi-value').forEach(el => {
        el.textContent = 'Error';
    });
    console.error('Dashboard Error:', message);
}

// Setup event listeners
function setupEventListeners() {
    // Year filter
    document.querySelectorAll('.year-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.year-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilters.year = this.dataset.year;
            applyFilters();
        });
    });

    // Month filter
    document.querySelectorAll('.month-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.month-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilters.month = this.dataset.month;
            applyFilters();
        });
    });

    // Sifat pekerjaan filter
    document.querySelectorAll('.sifat-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.sifat-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilters.sifat = this.dataset.sifat;
            applyFilters();
        });
    });

    // Status filter
    document.querySelectorAll('.status-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.status-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilters.status = this.dataset.status;
            applyFilters();
        });
    });
}

// Apply filters to data
function applyFilters() {
    filteredData = allData.filter(item => {
        let matches = true;

        // Filter by year - using correct field names
        if (currentFilters.year) {
            const tahun = item['TAHUN'] || item.tahun || '';
            if (tahun.toString() !== currentFilters.year) {
                matches = false;
            }
        }

        // Filter by month - using correct field names
        if (currentFilters.month) {
            const bulan = item['BULAN'] || item.bulan || '';
            if (bulan !== currentFilters.month) {
                matches = false;
            }
        }

        // Filter by sifat pekerjaan - using correct field names
        if (currentFilters.sifat) {
            const sifatPekerjaan = item['SIFAT PEKERJAAN'] || item.sifat_pekerjaan || '';
            if (sifatPekerjaan.toUpperCase() !== currentFilters.sifat.toUpperCase()) {
                matches = false;
            }
        }

        // Filter by status - using correct field names
        if (currentFilters.status) {
            const status = item['STATUS'] || item.status || '';
            if (status.toUpperCase() !== currentFilters.status.toUpperCase()) {
                matches = false;
            }
        }

        // Filter by lokasi - using correct field names
        if (currentFilters.lokasi) {
            const lokasi = item['LOKASI GI / GIS / GITET'] || item.lokasi || '';
            if (lokasi !== currentFilters.lokasi) {
                matches = false;
            }
        }

        return matches;
    });

    console.log('Filtered data:', filteredData.length, 'of', allData.length, 'records');
    updateDashboard();
}

// Update dashboard with filtered data
function updateDashboard() {
    updateKPICards();
    updateCharts();
    updateEquipmentPanel();
    updateSifatPekerjaanStats();
}

// Update KPI cards in header
function updateKPICards() {
    const stats = calculateStats(filteredData);
    
    document.getElementById('header-anomali').textContent = stats.anomali;
    document.getElementById('header-ganti-mtu').textContent = stats.gantiMtu;
    document.getElementById('header-rutin').textContent = stats.rutin;
    document.getElementById('header-non-rutin').textContent = stats.nonRutin;
    document.getElementById('header-total-har').textContent = stats.total;
    document.getElementById('header-total').textContent = stats.totalGI;
    
    // Update progress
    const progressPercentage = stats.total > 0 ? Math.round((stats.selesai / stats.total) * 100) : 0;
    document.getElementById('progress-percentage').textContent = progressPercentage + '%';
    
    // Update progress chart
    updateProgressChart(progressPercentage);
}

// Calculate statistics from data
function calculateStats(data) {
    const stats = {
        anomali: 0,
        gantiMtu: 0,
        rutin: 0,
        nonRutin: 0,
        total: data.length,
        selesai: 0,
        belumSelesai: 0,
        totalGI: 0
    };

    const uniqueGI = new Set();

    data.forEach(item => {
        // Count by sifat pekerjaan - using the correct field names from Excel
        const sifatPekerjaan = item['SIFAT PEKERJAAN'] || item.sifat_pekerjaan || '';
        switch(sifatPekerjaan.toUpperCase()) {
            case 'ANOMALI':
                stats.anomali++;
                break;
            case 'GANTI MTU':
                stats.gantiMtu++;
                break;
            case 'RUTIN':
                stats.rutin++;
                break;
            case 'NON RUTIN':
                stats.nonRutin++;
                break;
        }

        // Count by status - using the correct field names from Excel
        const status = item['STATUS'] || item.status || '';
        if (status.toUpperCase() === 'SELESAI') {
            stats.selesai++;
        } else {
            stats.belumSelesai++;
        }

        // Count unique GI - using the correct field names from Excel
        const lokasi = item['LOKASI GI / GIS / GITET'] || item.lokasi || '';
        if (lokasi) {
            uniqueGI.add(lokasi);
        }
    });

    stats.totalGI = uniqueGI.size;
    console.log('Calculated stats:', stats); // Debug log
    return stats;
}

// Update progress chart
function updateProgressChart(percentage) {
    const canvas = document.getElementById('progress-chart');
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background circle
    ctx.beginPath();
    ctx.arc(30, 30, 25, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 4;
    ctx.stroke();
    
    // Draw progress arc
    const angle = (percentage / 100) * 2 * Math.PI;
    ctx.beginPath();
    ctx.arc(30, 30, 25, -Math.PI / 2, -Math.PI / 2 + angle);
    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.stroke();
}

// Update charts
function updateCharts() {
    updateJenisChart();
    updateStatusChart();
    updateMainChart();
}

// Update jenis pemeliharaan chart
function updateJenisChart() {
    const canvas = document.getElementById('jenis-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas size explicitly
    canvas.width = 160;
    canvas.height = 160;
    canvas.style.width = '160px';
    canvas.style.height = '160px';
    
    if (window.jenisChart) {
        window.jenisChart.destroy();
    }
    
    const stats = calculateStats(filteredData);
    const data = [stats.rutin, stats.anomali, stats.gantiMtu, stats.nonRutin];
    const total = data.reduce((a, b) => a + b, 0);
    
    window.jenisChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['RUTIN', 'ANOMALI', 'GANTI MTU', 'NON RUTIN'],
            datasets: [{
                data: data,
                backgroundColor: ['#2ed573', '#ff4757', '#ff6b9d', '#747d8c'],
                borderWidth: 0,
                cutout: '60%'
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            layout: {
                padding: 10
            }
        }
    });
    
    // Update legend percentages
    const legendItems = document.querySelectorAll('.pie-chart-container:first-child .legend-value');
    if (total > 0) {
        legendItems[0].textContent = Math.round((stats.rutin / total) * 100) + '%';
        legendItems[1].textContent = Math.round((stats.anomali / total) * 100) + '%';
        legendItems[2].textContent = Math.round((stats.gantiMtu / total) * 100) + '%';
    }
}

// Update status chart
function updateStatusChart() {
    const canvas = document.getElementById('status-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas size explicitly
    canvas.width = 160;
    canvas.height = 160;
    canvas.style.width = '160px';
    canvas.style.height = '160px';
    
    if (window.statusChart) {
        window.statusChart.destroy();
    }
    
    const stats = calculateStats(filteredData);
    
    window.statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['SELESAI', 'BELUM SELESAI'],
            datasets: [{
                data: [stats.selesai, stats.belumSelesai],
                backgroundColor: ['#2ed573', '#ff4757'],
                borderWidth: 0,
                cutout: '60%'
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            layout: {
                padding: 10
            }
        }
    });
    
    // Update legend values
    const legendItems = document.querySelectorAll('.pie-chart-container:last-child .legend-value');
    legendItems[0].textContent = stats.selesai;
    legendItems[1].textContent = stats.belumSelesai;
}

// Update main bar chart
function updateMainChart() {
    const canvas = document.getElementById('main-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas size explicitly
    canvas.style.width = '100%';
    canvas.style.height = '250px';
    
    if (window.mainChart) {
        window.mainChart.destroy();
    }
    
    // Group data by location
    const locationData = {};
    filteredData.forEach(item => {
        const lokasi = item['LOKASI GI / GIS / GITET'] || item.lokasi || 'Unknown';
        const sifatPekerjaan = item['SIFAT PEKERJAAN'] || item.sifat_pekerjaan || '';
        
        if (!locationData[lokasi]) {
            locationData[lokasi] = {
                anomali: 0,
                gantiMtu: 0,
                nonRutin: 0,
                rutin: 0
            };
        }
        
        switch(sifatPekerjaan.toUpperCase()) {
            case 'ANOMALI':
                locationData[lokasi].anomali++;
                break;
            case 'GANTI MTU':
                locationData[lokasi].gantiMtu++;
                break;
            case 'NON RUTIN':
                locationData[lokasi].nonRutin++;
                break;
            case 'RUTIN':
                locationData[lokasi].rutin++;
                break;
        }
    });
    
    const locations = Object.keys(locationData);
    const anomaliData = locations.map(loc => locationData[loc].anomali);
    const gantiMtuData = locations.map(loc => locationData[loc].gantiMtu);
    const nonRutinData = locations.map(loc => locationData[loc].nonRutin);
    const rutinData = locations.map(loc => locationData[loc].rutin);
    
    window.mainChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: locations,
            datasets: [
                {
                    label: 'ANOMALI',
                    data: anomaliData,
                    backgroundColor: '#ff4757',
                    borderWidth: 0
                },
                {
                    label: 'GANTI MTU',
                    data: gantiMtuData,
                    backgroundColor: '#ff6b9d',
                    borderWidth: 0
                },
                {
                    label: 'NON RUTIN',
                    data: nonRutinData,
                    backgroundColor: '#747d8c',
                    borderWidth: 0
                },
                {
                    label: 'RUTIN',
                    data: rutinData,
                    backgroundColor: '#2ed573',
                    borderWidth: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        color: '#ffffff',
                        maxRotation: 45
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    stacked: true,
                    ticks: {
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Update sifat pekerjaan stats in sidebar
function updateSifatPekerjaanStats() {
    const stats = calculateStats(filteredData);
    
    // Update sifat pekerjaan buttons with counts
    const sifatButtons = document.querySelectorAll('.sifat-btn');
    sifatButtons.forEach(btn => {
        const sifat = btn.dataset.sifat;
        let count = 0;
        
        switch(sifat) {
            case 'ANOMALI':
                count = stats.anomali;
                break;
            case 'GANTI MTU':
                count = stats.gantiMtu;
                break;
            case 'NON RUTIN':
                count = stats.nonRutin;
                break;
            case 'RUTIN':
                count = stats.rutin;
                break;
        }
        
        // Add count to button if not already present
        if (!btn.querySelector('.count')) {
            const countSpan = document.createElement('span');
            countSpan.className = 'count';
            btn.appendChild(countSpan);
        }
        btn.querySelector('.count').textContent = count;
    });
}

// Populate location list in right panel
function populateLocationList() {
    const locationList = document.getElementById('location-list');
    const locationData = {};
    
    // Count items per location and categorize by sifat pekerjaan
    allData.forEach(item => {
        const lokasi = item['LOKASI GI / GIS / GITET'] || item.lokasi || '';
        const sifat = item['SIFAT PEKERJAAN'] || item.sifat_pekerjaan || '';
        
        if (lokasi) {
            if (!locationData[lokasi]) {
                locationData[lokasi] = {
                    total: 0,
                    anomali: 0,
                    gantiMtu: 0,
                    nonRutin: 0,
                    rutin: 0
                };
            }
            
            locationData[lokasi].total++;
            
            switch(sifat.toUpperCase()) {
                case 'ANOMALI':
                    locationData[lokasi].anomali++;
                    break;
                case 'GANTI MTU':
                    locationData[lokasi].gantiMtu++;
                    break;
                case 'NON RUTIN':
                    locationData[lokasi].nonRutin++;
                    break;
                case 'RUTIN':
                    locationData[lokasi].rutin++;
                    break;
            }
        }
    });
    
    // Sort locations by total count (descending)
    const sortedLocations = Object.entries(locationData)
        .sort(([,a], [,b]) => b.total - a.total);
    
    locationList.innerHTML = '';
    sortedLocations.forEach(([location, data]) => {
        const locationItem = document.createElement('div');
        locationItem.className = 'location-item clickable';
        locationItem.innerHTML = `
            <div class="location-header">
                <span class="location-name">${location}</span>
                <span class="location-count">${data.total}</span>
            </div>
            <div class="location-details">
                <span class="detail-text">Kegiatan Pemeliharaan</span>
                <i class="fas fa-chevron-down expand-icon"></i>
            </div>
            <div class="location-chart-container" style="display: none;">
                <canvas class="location-mini-chart" width="200" height="100"></canvas>
                <div class="mini-chart-legend">
                    <div class="mini-legend-item"><span class="mini-dot anomali-dot"></span>Anomali: ${data.anomali}</div>
                    <div class="mini-legend-item"><span class="mini-dot ganti-mtu-dot"></span>Ganti MTU: ${data.gantiMtu}</div>
                    <div class="mini-legend-item"><span class="mini-dot non-rutin-dot"></span>Non Rutin: ${data.nonRutin}</div>
                    <div class="mini-legend-item"><span class="mini-dot rutin-dot"></span>Rutin: ${data.rutin}</div>
                </div>
            </div>
        `;
        
        // Add click event listener
        locationItem.addEventListener('click', function() {
            toggleLocationChart(this, data);
        });
        
        locationList.appendChild(locationItem);
    });
}

// Toggle location chart visibility and create chart
function toggleLocationChart(locationItem, data) {
    const chartContainer = locationItem.querySelector('.location-chart-container');
    const expandIcon = locationItem.querySelector('.expand-icon');
    const canvas = locationItem.querySelector('.location-mini-chart');
    
    if (chartContainer.style.display === 'none') {
        chartContainer.style.display = 'block';
        expandIcon.classList.add('expanded');
        
        // Create mini chart
        createLocationMiniChart(canvas, data);
    } else {
        chartContainer.style.display = 'none';
        expandIcon.classList.remove('expanded');
        
        // Destroy existing chart if any
        if (canvas.chart) {
            canvas.chart.destroy();
        }
    }
}

// Create mini chart for location
function createLocationMiniChart(canvas, data) {
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if any
    if (canvas.chart) {
        canvas.chart.destroy();
    }
    
    canvas.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Anomali', 'Ganti MTU', 'Non Rutin', 'Rutin'],
            datasets: [{
                data: [data.anomali, data.gantiMtu, data.nonRutin, data.rutin],
                backgroundColor: ['#ff4757', '#ff6b9d', '#747d8c', '#2ed573'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Populate lokasi buttons in bottom left
function populateLokasiButtons() {
    const lokasiButtons = document.getElementById('lokasi-buttons');
    const uniqueLocations = [...new Set(allData.map(item => {
        return item['LOKASI GI / GIS / GITET'] || item.lokasi || '';
    }))].filter(Boolean);
    
    lokasiButtons.innerHTML = '';
    
    // Add "Semua" option
    const semuaBtn = document.createElement('button');
    semuaBtn.className = 'lokasi-btn active';
    semuaBtn.dataset.lokasi = '';
    semuaBtn.textContent = 'SEMUA';
    semuaBtn.addEventListener('click', function() {
        document.querySelectorAll('.lokasi-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentFilters.lokasi = this.dataset.lokasi;
        applyFilters();
    });
    lokasiButtons.appendChild(semuaBtn);
    
    uniqueLocations.forEach(location => {
        const btn = document.createElement('button');
        btn.className = 'lokasi-btn';
        btn.dataset.lokasi = location;
        btn.textContent = location;
        btn.addEventListener('click', function() {
            document.querySelectorAll('.lokasi-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilters.lokasi = this.dataset.lokasi;
            applyFilters();
        });
        lokasiButtons.appendChild(btn);
    });
}

// Update equipment panel with bar chart
function updateEquipmentPanel() {
    const equipmentData = {};
    
    // Count equipment from filtered data
    filteredData.forEach(item => {
        const peralatan = item['KATEGORI'] || item.kategori || item['BAY / PHT'] || '';
        if (peralatan) {
            const equipType = peralatan.toUpperCase();
            if (!equipmentData[equipType]) {
                equipmentData[equipType] = {
                    count: 0,
                    status: 'Normal'
                };
            }
            equipmentData[equipType].count++;
        }
    });
    
    // Define equipment types and their colors
    const equipmentTypes = {
        'IBT': { name: 'IBT', color: '#ff9500' },
        'TRAFO': { name: 'TRAFO', color: '#ff4757' },
        'PMT': { name: 'PMT', color: '#ff6b9d' },
        'PMS': { name: 'PMS', color: '#00d2d3' },
        'LA': { name: 'LA', color: '#2ed573' },
        'CT': { name: 'CT', color: '#5352ed' },
        'BAY': { name: 'BAY', color: '#ffa502' }
    };
    
    // Prepare chart data
    const labels = [];
    const data = [];
    const backgroundColors = [];
    
    Object.entries(equipmentTypes).forEach(([type, config]) => {
        const count = equipmentData[type] ? equipmentData[type].count : 0;
        labels.push(config.name);
        data.push(count);
        backgroundColors.push(config.color);
    });
    
    // Create or update chart
    const canvas = document.getElementById('equipment-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if any
    if (window.equipmentChart) {
        window.equipmentChart.destroy();
    }
    
    window.equipmentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Jumlah Equipment',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color + '80'),
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#333',
                    borderWidth: 1,
                    cornerRadius: 6,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + ' unit';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: '#ffffff',
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    }
                },
                x: {
                    ticks: {
                        color: '#ffffff',
                        font: {
                            size: 11,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10,
                    left: 10,
                    right: 10
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutBounce',
                delay: (context) => {
                    let delay = 0;
                    if (context.type === 'data' && context.mode === 'default') {
                        delay = context.dataIndex * 200;
                    }
                    return delay;
                },
                onComplete: () => {
                    // Add pulsing animation to bars
                    const chart = window.equipmentChart;
                    if (chart) {
                        setInterval(() => {
                            chart.update('none');
                        }, 3000);
                    }
                }
            },
            hover: {
                animationDuration: 300
            },
            transitions: {
                active: {
                    animation: {
                        duration: 400
                    }
                }
            }
        }
    });
}

// Update date time
function updateDateTime() {
    const now = new Date();
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Asia/Jakarta'
    };
    
    const formatter = new Intl.DateTimeFormat('id-ID', options);
    const formattedDate = formatter.format(now);
    
    document.getElementById('ultg-datetime').textContent = formattedDate + ' WIB';
}

