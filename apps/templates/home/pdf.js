window.onload = function () {
    document.getElementById("generate-pdf")
        .addEventListener("click", () => {
            const report = this.document.getElementById("report-div");
            console.log(report);
            console.log(window);
            var opt = {
                margin: 1,
                filename: 'report.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().from(report).set(opt).save();
        })
}