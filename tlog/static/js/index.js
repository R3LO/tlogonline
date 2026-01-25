// Mobile-optimized autocomplete for callsign input
document.addEventListener('DOMContentLoaded', function() {
    const myCallsignInput = document.getElementById('my_callsign');
    const suggestionsBox = document.getElementById('callsignSuggestions');
    const callsignInput = document.getElementById('callsign');
    let debounceTimer;

    if (!myCallsignInput || !suggestionsBox) {
        return; // Elements not found, exit
    }

    myCallsignInput.addEventListener('input', function() {
        const query = this.value.trim().toUpperCase();

        clearTimeout(debounceTimer);

        if (query.length < 1) {
            suggestionsBox.innerHTML = '';
            suggestionsBox.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch('/search-callsigns/?q=' + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';
                    if (data.callsigns && data.callsigns.length > 0) {
                        suggestionsBox.style.display = 'block';
                        data.callsigns.forEach(callsign => {
                            const item = document.createElement('button');
                            item.type = 'button';
                            item.className = 'list-group-item list-group-item-action';
                            item.textContent = callsign;
                            item.addEventListener('click', function() {
                                myCallsignInput.value = callsign;
                                suggestionsBox.innerHTML = '';
                                suggestionsBox.style.display = 'none';
                            });
                            suggestionsBox.appendChild(item);
                        });
                    } else {
                        suggestionsBox.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    suggestionsBox.style.display = 'none';
                });
        }, 300);
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (myCallsignInput && suggestionsBox) {
            if (!myCallsignInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.style.display = 'none';
            }
        }
    });

    // Handle search form submission
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const myCallsign = myCallsignInput.value.trim().toUpperCase();
            const searchCallsign = callsignInput.value.trim().toUpperCase();

            if (!myCallsign) {
                alert('Введите позывной пользователя');
                return;
            }

            const url = '/' + myCallsign + '/?callsign=' + encodeURIComponent(searchCallsign);
            window.location.href = url;
        });
    }
});