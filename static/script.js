document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading indicator
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    
    // Get form data
    const formData = {
        sport: document.getElementById('sport').value,
        player: document.getElementById('player').value,
        line: document.getElementById('line').value
    };
    
    try {
        // Send analysis request
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        // Hide loading indicator
        document.getElementById('loading').classList.add('hidden');
        
        // Display results
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').classList.add('hidden');
        alert('An error occurred while analyzing. Please try again.');
    }
});

function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    
    // Clear previous results
    resultsContent.innerHTML = '';
    
    if (data.success) {
        // Create result card
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Add result items
        const items = [
            ['Player', data.player_name],
            ['Average Performance', data.avg_performance.toFixed(2)],
            ['Betting Line', data.betting_line],
            ['Performance Difference', data.performance_diff.toFixed(2)]
        ];
        
        items.forEach(([label, value]) => {
            const item = document.createElement('div');
            item.className = 'result-item';
            item.innerHTML = `
                <span class="result-label">${label}:</span>
                <span class="result-value">${value}</span>
            `;
            card.appendChild(item);
        });
        
        // Add recommendation
        const recommendation = document.createElement('div');
        recommendation.className = `recommendation ${data.recommendation.toLowerCase()}`;
        recommendation.textContent = `Recommendation: ${data.recommendation}`;
        card.appendChild(recommendation);
        
        resultsContent.appendChild(card);
    } else {
        resultsContent.innerHTML = `
            <div class="bg-red-100 text-red-800 p-4 rounded-lg">
                Error: ${data.error}
            </div>
        `;
    }
    
    resultsDiv.classList.remove('hidden');
}
