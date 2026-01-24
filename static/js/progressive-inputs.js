/**
 * Progressive Bullet Inputs (TOUCH-03)
 * Start with 1 visible input. Reveal next when user types in current last visible.
 * Max 5 inputs. Existing data shows all populated inputs immediately.
 */
(function() {
    'use strict';

    var SELECTOR = '.bullet-input';
    var HIDDEN_CLASS = 'bullet-input-hidden';
    var REVEAL_CLASS = 'bullet-input-reveal';

    function initProgressiveInputs() {
        var inputs = document.querySelectorAll(SELECTOR);
        if (inputs.length === 0) return;

        // Determine which inputs have pre-existing values (edit mode / draft restore)
        var lastPopulatedIndex = -1;
        inputs.forEach(function(input, idx) {
            if (input.value.trim().length > 0) {
                lastPopulatedIndex = idx;
            }
        });

        // Show inputs up to lastPopulated + 1 (so next empty one is visible)
        // Minimum: always show first input
        var showUpTo = Math.max(0, lastPopulatedIndex + 1);

        inputs.forEach(function(input, idx) {
            if (idx <= showUpTo) {
                // Visible — no hidden class, no animation (already populated or first)
                input.classList.remove(HIDDEN_CLASS);
            } else {
                // Hidden — will reveal progressively
                input.classList.add(HIDDEN_CLASS);
            }
        });

        // Attach input listeners for progressive reveal
        inputs.forEach(function(input, idx) {
            input.addEventListener('input', function() {
                revealNext(inputs, idx);
            });
        });
    }

    function revealNext(inputs, currentIdx) {
        // Only reveal next if current input has content
        if (inputs[currentIdx].value.trim().length === 0) return;

        // Find the next hidden input
        var nextIdx = currentIdx + 1;
        if (nextIdx >= inputs.length) return;

        var nextInput = inputs[nextIdx];
        if (!nextInput.classList.contains(HIDDEN_CLASS)) return;

        // Reveal with animation
        nextInput.classList.remove(HIDDEN_CLASS);
        nextInput.classList.add(REVEAL_CLASS);

        // Remove animation class after it completes (so it doesn't replay)
        nextInput.addEventListener('animationend', function handler() {
            nextInput.classList.remove(REVEAL_CLASS);
            nextInput.removeEventListener('animationend', handler);
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProgressiveInputs);
    } else {
        initProgressiveInputs();
    }
})();
