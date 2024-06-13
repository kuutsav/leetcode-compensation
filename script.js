// Min Data points for box plot
const minDataPoints = 3;

// Set of roles to display in the box plot
const validRoles = new Set([
    'SDE I',
    'SDE II',
    'SDE III',
    "Staff Engineer",
    "MTS I",
    "MTS II",
    "MTS III",
    "Data Scientist",
    "Data Engineer",
    "Associate Software Engineer",
    "Analyst",
]);

const offersPerPage = 10;

// Utility function to capitalize the first letter of a string
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function statsStr(data) {
    const nRecs = data.length;
    startDate = data[0].creation_date;
    endDate = data[nRecs - 1].creation_date;
    return `
    Based on ${nRecs} recs parsed between ${startDate} and ${endDate}
    (only includes posts that were parsed successfully and had non negative votes)
    `;
}

function formatSalaryInINR(lpa) {
    // Convert LPA to total rupees
    const totalRupees = Math.ceil(lpa * 100000);
    let rupeesStr = totalRupees.toString();
    let lastThree = rupeesStr.substring(rupeesStr.length - 3);
    const otherNumbers = rupeesStr.substring(0, rupeesStr.length - 3);
    if (otherNumbers != '') {
        lastThree = ',' + lastThree;
    }
    let formattedSalary = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + lastThree;
    return `₹${formattedSalary}`;
}

function extractValues(data, key) {
    return data.map(item => item[key]);
}

function calculateFrequencies(values) {
    return values.reduce((acc, value) => {
        const bin = Math.floor(value / 10);
        acc[bin] = (acc[bin] || 0) + 1;
        return acc;
    }, {});
}

function prepareChartData(frequencies) {
    return Object.entries(frequencies)
        .sort(([a], [b]) => a - b)
        .map(([bin, count]) => ({
            name: `${bin * 10}-${bin * 10 + 9}`,
            y: count
        }));
}

function initializeHistogramChart(chartData, baseOrTotal) {
    Highcharts.chart('salaryBarPlot', {
        chart: { type: 'column' },
        title: { text: '' },
        xAxis: {
            type: 'category',
            title: { text: `${capitalize(baseOrTotal)} Compensation (₹ LPA)` },
            labels: { rotation: 0 }
        },
        yAxis: { title: { text: '' } },
        legend: { enabled: false },
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: { enabled: true, format: '{point.y}' }
            }
        },
        series: [{ name: 'Total', data: chartData, color: '#55b17f' }]
    });
}

function mostOfferCompanies(jsonData) {
    const companyCounts = countCompanies(jsonData);
    let [categories, counts] = sortAndSliceData(companyCounts);

    initializeBarChart(categories, counts);
}

function countCompanies(data) {
    return data.reduce((acc, { company }) => {
        acc[company] = (acc[company] || 0) + 1;
        return acc;
    }, {});
}

function sortAndSliceData(companyCounts) {
    const sortedData = Object.entries(companyCounts)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10);

    const categories = sortedData.map(([company]) => company);
    const counts = sortedData.map(([, count]) => count);

    return [categories, counts];
}

function initializeBarChart(categories, counts) {
    Highcharts.chart('companyBarPlot', {
        chart: { type: 'bar' },
        title: { text: '' },
        xAxis: {
            categories: categories,
            title: { text: null }
        },
        yAxis: {
            min: 0,
            title: { text: '# Offers', align: 'high' },
            labels: { overflow: 'justify' }
        },
        tooltip: { valueSuffix: ' occurrences' },
        plotOptions: { bar: { dataLabels: { enabled: true } } },
        legend: { enabled: false },
        series: [{ name: 'Offers', data: counts, color: '#55b17f' }]
    });
}

function plotHistogram(jsonData, baseOrTotal) {
    const totalValues = extractValues(jsonData, baseOrTotal);
    const totalFrequencies = calculateFrequencies(totalValues);
    const chartData = prepareChartData(totalFrequencies);

    initializeHistogramChart(chartData, baseOrTotal);
}

// Helper function to calculate quantiles
function quantile(arr, q) {
    const sorted = arr.slice().sort((a, b) => a - b);
    const pos = (sorted.length - 1) * q;
    const base = Math.floor(pos);
    const rest = pos - base;
    return sorted[base + 1] !== undefined ? sorted[base] + rest * (sorted[base + 1] - sorted[base]) : sorted[base];
}

// Function to group salary values by role or company
function groupSalariesBy(jsonData, groupBy, valueKey) {
    return jsonData.reduce((acc, item) => {
        const key = item[groupBy];
        const value = item[valueKey];
        if (!acc[key]) acc[key] = [];
        acc[key].push(value);
        return acc;
    }, {});
}

// Function to calculate the five-number summary for each group
function calculateBoxPlotData(salariesByGroup, validItems, minDataPoints = 3) {
    return Object.keys(salariesByGroup)
        .filter(key => salariesByGroup[key].length >= minDataPoints && (validItems.size === 0 || validItems.has(key)))
        .map(key => {
            const values = salariesByGroup[key];
            return {
                name: key,
                data: [[Math.min(...values), quantile(values, 0.25), quantile(values, 0.5), quantile(values, 0.75), Math.max(...values)]]
            };
        })
        .sort((a, b) => b.data[0][2] - a.data[0][2]) // Sort by median value
        .slice(0, 20); // Keep only the top 20
}

// Function to initialize the Highcharts chart for box plot
function initializeBoxPlotChart(docId, boxPlotData, baseOrTotal, roleOrCompany) {
    Highcharts.chart(docId, {
        chart: { type: 'boxplot' },
        title: { text: '' },
        legend: { enabled: false },
        xAxis: {
            categories: boxPlotData.map(item => item.name),
            title: { text: '' },
            labels: { rotation: -90 }
        },
        yAxis: {
            title: { text: `${capitalize(baseOrTotal)} Compensation (₹ LPA)` }
        },
        series: [{
            name: 'Salaries',
            data: boxPlotData.map(item => item.data[0]),
            tooltip: { headerFormat: `<em>${capitalize(roleOrCompany)}: {point.key}</em><br/>` },
            color: '#55b17f'
        }]
    });
}

function plotBoxPlot(jsonData, baseOrTotal, docId, roleOrCompany, validItems) {
    const salariesByGroup = groupSalariesBy(jsonData, roleOrCompany, baseOrTotal);
    const boxPlotData = calculateBoxPlotData(salariesByGroup, validItems);
    initializeBoxPlotChart(docId, boxPlotData, baseOrTotal, roleOrCompany);
}

document.addEventListener('DOMContentLoaded', async function () {
    let currentPage = 1;
    let offers = [];
    let filteredOffers = []; // New variable to hold filtered data

    // Fetch your JSONL data converted to JSON array
    async function fetchOffers() {
        const response = await fetch('data/parsed_comps.json');
        const data = await response.json();
        offers = data;

        filteredOffers = [...offers];
        displayOffers(currentPage);
    }

    await fetchOffers();

    let statsInfo = statsStr(offers);

    document.getElementById('statsStr').textContent = statsInfo;
    plotHistogram(filteredOffers, 'total');
    mostOfferCompanies(filteredOffers);
    plotBoxPlot(filteredOffers, 'total', 'companyBoxPlot', 'company', new Set([]));
    plotBoxPlot(filteredOffers, 'total', 'roleBoxPlot', 'mapped_role', validRoles);

    function displayOffers(page) {
        const startIndex = (page - 1) * offersPerPage;
        const endIndex = startIndex + offersPerPage;
        const paginatedOffers = filteredOffers.slice(startIndex, endIndex);

        const table = document.createElement('table');
        table.classList.add('table');
        const emptyRow = table.insertRow();
        emptyRow.innerHTML = `
        <th style="width: 5%"></th><th style="width: 15%"></th>
        <th style="width: 30%"></th><th style="width: 25%"></th>
        <th style="width: 5%"></th><th style="width: 20%"></th>
        `;
        const headerRow = table.insertRow();
        headerRow.style.border = 'none';
        const indexHeader = headerRow.insertCell();
        indexHeader.innerHTML = '<b style="font-size: 13px;">#</b>';
        const idHeader = headerRow.insertCell();
        idHeader.innerHTML = '<b style="font-size: 13px;">ID</b>';
        const companyHeader = headerRow.insertCell();
        companyHeader.innerHTML = `
        <b style="font-size: 13px;">Company<br>
        <span class="text-secondary">Location | Date</span></b>
        `;
        const roleHeader = headerRow.insertCell();
        roleHeader.innerHTML = '<b style="font-size: 13px;">Role</b>';
        const yoeHeader = headerRow.insertCell();
        yoeHeader.innerHTML = '<b style="font-size: 13px;">Yoe</b>';
        const salaryHeader = headerRow.insertCell();
        salaryHeader.innerHTML = `
        <p class="text-end" style="margin-bottom: 0px;">
        <b style="font-size: 13px;">Total<br>
        <span class="text-secondary">Base</span></b></p>
        `;

        paginatedOffers.forEach((offer, index) => {
            const row = table.insertRow();
            const indexCell = row.insertCell();
            indexCell.innerHTML = `<p>${startIndex + index + 1}</p>`;
            const idCell = row.insertCell();
            idCell.innerHTML = `
            <p><abbr title="attribute">
            <a class="link-secondary" href="https://leetcode.com/discuss/compensation/${offer.id}">
            ${offer.id}
            </a></abbr></p>
            `;
            const companyCell = row.insertCell();
            companyCell.innerHTML = `
            <b style="font-size: 13px;">${offer.company}</b>
            <br><span class="text-secondary">
            ${offer.location} | ${offer.creation_date}
            </span>`;
            const roleCell = row.insertCell();
            roleCell.innerHTML = `
            <b style="font-size: 13px;">${offer.mapped_role}</b>
            <br><span class="text-secondary">${offer.role}</span>`;
            const yoeCell = row.insertCell();
            yoeCell.textContent = offer.yoe;
            const salaryCell = row.insertCell();
            salaryCell.innerHTML = `
            <p class="text-end" style="margin-bottom: 0px;">
            <b style="font-size: 13px;">${formatSalaryInINR(offer.total)}</b>
            <br><span class="text-secondary" style="font-size: 13px;">
            ${formatSalaryInINR(offer.base)}</span></p>
            `;
        });

        const container = document.getElementById('offersTable');
        container.innerHTML = '';
        container.appendChild(table);
    }

    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayOffers(currentPage);
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        if ((currentPage * offersPerPage) < offers.length) {
            currentPage++;
            displayOffers(currentPage);
        }
    });

    // Function to filter offers by company name
    function filterOffersByCompany(companyName) {
        if (companyName.trim() === '') {
            filteredOffers = [...offers]; // Reset filteredOffers to all data if search input is empty
        } else {
            filteredOffers = offers.filter(offer => offer.company.toLowerCase().includes(companyName.toLowerCase()));
        }

        // Update graphs with filtered data
        plotHistogram(filteredOffers, 'total');
        mostOfferCompanies(filteredOffers);
        plotBoxPlot(filteredOffers, 'total', 'companyBoxPlot', 'company', new Set([]));
        plotBoxPlot(filteredOffers, 'total', 'roleBoxPlot', 'mapped_role', validRoles);

        // Update offers table with filtered data
        displayOffers(currentPage);
    }

    // Search by button
    document.getElementById('searchButton').addEventListener('click', () => {
        const searchInput = document.getElementById('searchInput').value;
        filterOffersByCompany(searchInput);
    });

    // Search By enter
    document.getElementById('searchInput').addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            const searchInput = document.getElementById('searchInput').value;
            filterOffersByCompany(searchInput);
        }
    });
});
