// Constants and Variables
const minDataPointsForBoxPlot = 2;
const validYoeBucket = new Set(["Entry (0-1)", "Mid (2-6)", "Senior (7-10)", "Senior + (10+)"]);
const offersPerPage = 10;
let currentPage = 1;
let offers = [];
let filteredOffers = [];
let currentSort = { column: null, order: 'asc' };
let totalPages = 0;
let barChartFilterIsSet = false;
const svgWidth = 16;
const svgHeight = 16;

const resetSvg = `<svg width=${svgWidth} height=${svgHeight} fill="#000000" viewBox="0 0 32 32" id="icon" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <defs> <style> .cls-1 { fill: none; } </style> </defs> <path d="M22.5,9A7.4522,7.4522,0,0,0,16,12.792V8H14v8h8V14H17.6167A5.4941,5.4941,0,1,1,22.5,22H22v2h.5a7.5,7.5,0,0,0,0-15Z"></path> <path d="M26,6H4V9.171l7.4142,7.4143L12,17.171V26h4V24h2v2a2,2,0,0,1-2,2H12a2,2,0,0,1-2-2V18L2.5858,10.5853A2,2,0,0,1,2,9.171V6A2,2,0,0,1,4,4H26Z"></path> <rect id="_Transparent_Rectangle_" data-name="<Transparent Rectangle>" class="cls-1" width="32" height="32"></rect> </g></svg>`;

// Utility Functions
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function setStatsStr(data) {
    const nRecs = data.length;
    const startDate = data[0].creation_date;
    const endDate = data[nRecs - 1].creation_date;
    let statsStr = `Based on ${nRecs} recs parsed between ${startDate} and ${endDate} (only includes posts that were parsed successfully and had non negative votes)`;
    document.getElementById('statsStr').textContent = statsStr;
}

function formatSalaryInINR(lpa) {
    const totalRupees = Math.ceil(lpa * 100000);
    let rupeesStr = totalRupees.toString();
    let lastThree = rupeesStr.substring(rupeesStr.length - 3);
    const otherNumbers = rupeesStr.substring(0, rupeesStr.length - 3);
    if (otherNumbers != '') lastThree = ',' + lastThree;
    return `₹${otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + lastThree}`;
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
    return Object.entries(frequencies).sort(([a], [b]) => a - b).map(([bin, count]) => ({
        name: `${bin * 10}-${bin * 10 + 9}`,
        y: count
    }));
}

// Highcharts Initialization Functions
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
                cursor: 'pointer',
                dataLabels: { enabled: true, format: '{point.y}' },
                point: {
                    events: {
                        click: function () {
                            if (barChartFilterIsSet) {
                                alert("Please reset the previous filter first or refresh the page")
                                return;
                            }
                            const rangeString = this?.name;
                            const [start, end] = rangeString.split("-").map(r => parseInt(r));
                            const filteredCompensation = filteredOffers.filter(compensation => {
                                return compensation.total >= start && compensation.total <= end;
                            });
                            setResetButtonVisibility(true, rangeString);
                            filteredOffers = filteredCompensation;
                            setStatsStr(filteredOffers);
                            displayOffers(1);
                            document.getElementById("offersTable").scrollIntoView();
                            barChartFilterIsSet = true;
                        }
                    }
                }
            }
        },
        series: [{ name: 'Total', data: chartData, color: '#55b17f' }],

    });
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

// Data Processing Functions
function quantile(arr, q) {
    const sorted = arr.slice().sort((a, b) => a - b);
    const pos = (sorted.length - 1) * q;
    const base = Math.floor(pos);
    const rest = pos - base;
    return sorted[base + 1] !== undefined ? sorted[base] + rest * (sorted[base + 1] - sorted[base]) : sorted[base];
}

function groupSalariesBy(jsonData, groupBy, valueKey) {
    return jsonData.reduce((acc, item) => {
        const key = item[groupBy];
        const value = item[valueKey];
        if (!acc[key]) acc[key] = [];
        acc[key].push(value);
        return acc;
    }, {});
}

function calculateBoxPlotData(salariesByGroup, validItems, minDataPoints = minDataPointsForBoxPlot) {
    return Object.keys(salariesByGroup).filter(key => salariesByGroup[key].length >= minDataPoints && (validItems.size === 0 || validItems.has(key))).map(key => {
        const values = salariesByGroup[key];
        return {
            name: key,
            data: [[Math.min(...values), quantile(values, 0.25), quantile(values, 0.5), quantile(values, 0.75), Math.max(...values)]]
        };
    }).sort((a, b) => b.data[0][2] - a.data[0][2]).slice(0, 20);
}

// Plotting Functions
function plotHistogram(jsonData, baseOrTotal) {
    const totalValues = extractValues(jsonData, baseOrTotal);
    const totalFrequencies = calculateFrequencies(totalValues);
    const chartData = prepareChartData(totalFrequencies);
    initializeHistogramChart(chartData, baseOrTotal);
}

function plotBoxPlot(jsonData, baseOrTotal, docId, roleOrCompany, validItems) {
    const salariesByGroup = groupSalariesBy(jsonData, roleOrCompany, baseOrTotal);
    const boxPlotData = calculateBoxPlotData(salariesByGroup, validItems);
    initializeBoxPlotChart(docId, boxPlotData, baseOrTotal, roleOrCompany);
}

function getSortArrow(column) {
    if (currentSort.column === column) {
        return currentSort.order === 'asc' ?
            `<svg width="${svgWidth}" height="${svgHeight}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M12 6V18M12 6L7 11M12 6L17 11" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>` :
            `<svg width="${svgWidth}" height="${svgHeight}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M12 6V18M12 18L7 13M12 18L17 13" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>`;
    }
    // Default state (no sorting)
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 24 24"><path d="M6 9l6-6 6 6z M18 15l-6 6-6-6z" fill="#000" /></svg>`;
}

// Display and Sorting Functions
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
    indexHeader.innerHTML = '<b style="font-size: 13px;" data-column="#">#</b>';
    const idHeader = headerRow.insertCell();
    idHeader.innerHTML = '<b style="font-size: 13px;">ID</b>';
    const companyHeader = headerRow.insertCell();
    companyHeader.innerHTML = `
    <b style="font-size: 13px;" >Company<br>
    <span class="text-secondary">Location | Date</span></b>
    `;
    const roleHeader = headerRow.insertCell();
    roleHeader.innerHTML = '<b style="font-size: 13px;" >Role</b>';
    const yoeHeader = headerRow.insertCell();
    yoeHeader.innerHTML = `<b style="font-size: 13px;" data-column="yoe" role="button"> Yoe ${getSortArrow('yoe')}</b>`;
    const salaryHeader = headerRow.insertCell();

    salaryHeader.innerHTML = `
    <p class="text-end" style="margin-bottom: 0px;">
    <b style="font-size: 13px;" data-column="total" role="button">${getSortArrow('total')} Total <br>
    <span class="text-secondary">Base</span></b></p>
    `;

    // Add event listeners to headers for sorting
    headerRow.querySelectorAll('b[data-column]').forEach(header => {
        header.addEventListener('click', () => {
            const column = header.getAttribute('data-column');
            if (column === '#') {
                removeSorting();
            } else if (column) {
                sortOffers(column);
            }
        });
    });

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
    renderPageOptions(); // Render page options

}

function sortOffers(column) {
    if (currentSort.column === column) {
        // Toggle order: desc -> asc -> no sorting
        if (currentSort.order === 'asc') {
            currentSort.column = null;
            currentSort.order = 'desc';
        } else if (currentSort.order === 'desc') {
            currentSort.order = 'asc'; // Set order to asc after desc
        } else {
            currentSort.order = 'desc'; // Default to asc when no sorting
        }
    } else {
        // Set new column and default to ascending order
        currentSort.column = column;
        currentSort.order = 'desc';
    }

    // Sort filteredOffers based on currentSort
    if (currentSort.column) {
        filteredOffers.sort((a, b) => {
            if (a[currentSort.column] < b[currentSort.column]) {
                return currentSort.order === 'asc' ? -1 : 1;
            } else if (a[currentSort.column] > b[currentSort.column]) {
                return currentSort.order === 'asc' ? 1 : -1;
            } else {
                return 0;
            }
        });
    } else {
        // Default sorting by id in descending order when no column is selected
        filteredOffers.sort((a, b) => b.id - a.id);
    }
    displayOffers(currentPage);
}

function renderPageOptions() {
    const pageSelect = document.getElementById('pageSelect');
    pageSelect.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        if (i === currentPage) {
            option.selected = true;
        }
        pageSelect.appendChild(option);
    }
}

// Used to set visibility of reset button
function setResetButtonVisibility(isVisible, filterString = ""){
    if (isVisible) {
        filterString = `${resetSvg} ${filterString} (₹ LPA)`;
        document.getElementById("resetButton").innerHTML = filterString;
    }
    document.getElementById("resetButton").style.visibility=isVisible?"visible":"hidden";
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

// Event Listeners and Initial Setup
document.addEventListener('DOMContentLoaded', async function () {
    // Set initial visibility of the reset button
    setResetButtonVisibility(false);

    // Reset button event listener
    document.getElementById("resetButton").addEventListener("click", () => {
        filteredOffers = offers;
        setStatsStr(filteredOffers);
        displayOffers(1);
        setResetButtonVisibility(false);
        barChartFilterIsSet = false;
    });

    // Fetch and display offers
    async function fetchOffers() {
        const response = await fetch('data/parsed_comps.json');
        const data = await response.json();
        offers = data;
        filteredOffers = [...offers];
        totalPages = Math.ceil(filteredOffers.length / offersPerPage);
        displayOffers(currentPage);
    }

    await fetchOffers();

    // Initialize charts and stats
    setStatsStr(filteredOffers);
    plotHistogram(filteredOffers, 'total');
    mostOfferCompanies(filteredOffers);
    plotBoxPlot(filteredOffers, 'total', 'companyBoxPlot', 'company', new Set([]));
    plotBoxPlot(filteredOffers, 'total', 'yoeBucketBoxPlot', 'mapped_yoe', validYoeBucket);

    // Pagination event listeners
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayOffers(currentPage);
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        if ((currentPage * offersPerPage) < filteredOffers.length) {
            currentPage++;
            displayOffers(currentPage);
        }
    });

    // Page selection dropdown event listener
    document.getElementById('pageSelect').addEventListener('change', (event) => {
        currentPage = parseInt(event.target.value);
        displayOffers(currentPage);
    });

    // Filter offers by company name
    function filterOffersByCompany(companyName) {
        currentSort = { column: null, order: 'asc' };

        if (companyName.trim() === '') {
            filteredOffers = [...offers]; // Reset filteredOffers to all data if search input is empty
        } else {
            filteredOffers = offers.filter(offer => offer.company.toLowerCase().includes(companyName.toLowerCase()));
        }

        totalPages = Math.ceil(filteredOffers.length / offersPerPage); // Update total pages
        currentPage = 1; // Reset to the first page after filtering

        // Update graphs and offers table with filtered data
        setStatsStr(filteredOffers);
        plotHistogram(filteredOffers, 'total');
        mostOfferCompanies(filteredOffers);
        plotBoxPlot(filteredOffers, 'total', 'companyBoxPlot', 'company', new Set([]));
        plotBoxPlot(filteredOffers, 'total', 'yoeBucketBoxPlot', 'mapped_yoe', validYoeBucket);
        displayOffers(currentPage);
    }

    // Search button event listener
    document.getElementById('searchButton').addEventListener('click', () => {
        const searchInput = document.getElementById('searchInput').value;
        filterOffersByCompany(searchInput);
    });

    // Search input "Enter" key event listener
    document.getElementById('searchInput').addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            const searchInput = document.getElementById('searchInput').value;
            filterOffersByCompany(searchInput);
        }
    });
});
