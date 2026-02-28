document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommendation-form');
    const topNInput = document.getElementById('top-n');
    const topNValue = document.getElementById('top-n-value');
    const resultsSection = document.getElementById('results');
    const loadingSection = document.getElementById('loading');
    const submitBtn = document.getElementById('submit-btn');
    const citySelect = document.getElementById('city');
    const cuisineSelect = document.getElementById('cuisine');

    // Fetch and populate metadata
    async function loadMetadata() {
        try {
            const response = await fetch('/metadata/filters');
            if (response.ok) {
                const { cities, cuisines } = await response.json();

                cities.forEach(city => {
                    const opt = document.createElement('option');
                    opt.value = opt.textContent = city;
                    citySelect.appendChild(opt);
                });

                cuisines.forEach(cuisine => {
                    const opt = document.createElement('option');
                    opt.value = opt.textContent = cuisine;
                    cuisineSelect.appendChild(opt);
                });
            }
        } catch (error) {
            console.error('Metadata load error:', error);
        }
    }
    loadMetadata();

    // Update range input value display
    topNInput.addEventListener('input', (e) => {
        topNValue.textContent = e.target.value;
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Prepare request payload
        const formData = new FormData(form);
        const cuisine = formData.get('cuisine');

        const payload = {
            city: formData.get('city') || null,
            cuisines: cuisine ? [cuisine] : null,
            min_rating: parseFloat(formData.get('min_rating')) || null,
            max_price_bucket: parseInt(formData.get('max_price_bucket')) || null,
            top_n: parseInt(formData.get('top_n')) || 5
        };

        // UI State: Loading
        resultsSection.innerHTML = '';
        resultsSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch recommendations');
            }

            const data = await response.json();
            displayResults(data.restaurants);
        } catch (error) {
            console.error('Error:', error);
            resultsSection.innerHTML = `<div class="error-message">Oops! ${error.message}</div>`;
            resultsSection.classList.remove('hidden');
        } finally {
            loadingSection.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });

    function displayResults(restaurants) {
        if (!restaurants || restaurants.length === 0) {
            resultsSection.innerHTML = '<div class="no-results">No restaurants found matching your criteria. Try adjusting your filters.</div>';
            resultsSection.classList.remove('hidden');
            return;
        }

        const template = document.getElementById('restaurant-card-template');

        restaurants.forEach((restaurant, index) => {
            const clone = template.content.cloneNode(true);
            const card = clone.querySelector('.card');

            // Fill data
            clone.querySelector('.restaurant-name').textContent = restaurant.name;
            clone.querySelector('.rating-value').textContent = restaurant.rating || 'N/A';
            clone.querySelector('.votes').textContent = restaurant.votes ? `(${restaurant.votes} votes)` : '';
            clone.querySelector('.area').textContent = restaurant.area || 'Unknown Area';
            clone.querySelector('.city').textContent = restaurant.city || '';

            // Cuisines
            const cuisinesContainer = clone.querySelector('.cuisines');
            restaurant.cuisines.forEach(cuisine => {
                const span = document.createElement('span');
                span.className = 'cuisine-tag';
                span.textContent = cuisine;
                cuisinesContainer.appendChild(span);
            });

            // Price Tier
            const priceTiers = {
                1: '₹ (Budget)',
                2: '₹₹ (Mid-Range)',
                3: '₹₹₹ (Upscale)',
                4: '₹₹₹₹ (Premium)'
            };
            clone.querySelector('.price-info .price-tier').textContent = priceTiers[restaurant.price_range] || 'Price varies';

            // Explanation
            const explanationText = clone.querySelector('.explanation-text');
            explanationText.textContent = restaurant.explanation || "Selected based on your rating and cuisine preferences.";

            // Match Score
            const matchScore = (restaurant.score * 100).toFixed(0);
            clone.querySelector('.match-score').textContent = matchScore;

            resultsSection.appendChild(clone);

            // Trigger animation with delay
            setTimeout(() => {
                const addedCard = resultsSection.querySelectorAll('.card')[index];
                if (addedCard) addedCard.classList.add('visible');
            }, index * 100);
        });

        resultsSection.classList.remove('hidden');
    }
});
