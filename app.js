document.addEventListener('DOMContentLoaded', () => {
    const sceneImage = document.getElementById('scene-image');
    const sceneText = document.getElementById('scene-text');
    const giftCard = document.getElementById('gift-card');
    const card = document.querySelector('.card');

    const scenes = [
        {
            // Cute Anime Scene
            image: "https://media.tenor.com/PZcI9H8Z0jAAAAAi/anime-happy.gif",
            text: "Happy Birthday Wasay! ✨",
            duration: 4000
        },
        {
            // Dudu Bubu Scene
            image: "https://media.tenor.com/aKFaZBrZ_zIAAAAi/dudu-bubu.gif",
            text: "Brought Dudu & Bubu to celebrate! 🐻🐼",
            duration: 4000
        },
        {
            // League of Legends Scene (Ahri/Poro vibe)
            image: "https://media.tenor.com/D4s2G3-GDEgAAAAi/league-of-legends-poro.gif",
            text: "May you reach Challenger this year! ⚔️",
            duration: 4000
        }
    ];

    let currentScene = 0;

    function playSequence() {
        if (currentScene < scenes.length) {
            // Setup next scene
            sceneImage.src = scenes[currentScene].image;
            sceneText.innerText = scenes[currentScene].text;

            // Fade in
            setTimeout(() => {
                sceneImage.classList.add('visible');
                sceneText.classList.add('visible');
            }, 100);

            // Wait for duration, then fade out
            setTimeout(() => {
                sceneImage.classList.remove('visible');
                sceneText.classList.remove('visible');
                
                // Wait for fade out to complete before next scene
                setTimeout(() => {
                    currentScene++;
                    playSequence();
                }, 1000);
            }, scenes[currentScene].duration);

        } else {
            // End of sequence, show final card
            sceneImage.src = "https://media.tenor.com/V-f_WwWzX-4AAAAC/stars-sparkle.gif"; // Nice sparkly background
            setTimeout(() => {
                sceneImage.classList.add('visible');
                giftCard.style.display = 'block';
            }, 100);
        }
    }

    // Start the video sequence
    setTimeout(playSequence, 500);

    // Card click logic
    if (card) {
        card.addEventListener('click', () => {
            card.classList.toggle('is-open');
        });
    }
});
