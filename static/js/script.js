document.getElementById('read-more-btn').addEventListener('click', function() {
    alert('Welcome to the game! Click on any stage to start learning.');
});

document.getElementById('chat-funza-btn').addEventListener('click', function() {
    alert('Funza AI is here to assist you! Ask any question.');
});

function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
}
