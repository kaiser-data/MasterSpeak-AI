document.getElementById("speech-upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(event.target);
    const content = formData.get("content");

    try {
        const response = await fetch("/api/speeches", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content }),
        });

        if (!response.ok) {
            throw new Error("Failed to analyze speech");
        }

        const data = await response.json();
        alert("Speech analyzed successfully!");
        window.location.reload(); // Reload the page to display updated results
    } catch (error) {
        alert(error.message);
    }
});