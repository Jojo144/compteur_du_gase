/** Génère un fichier HTML a la volée et le fait télécharger par le navigateur
 */
function downloadHTMLFile(data, documentTitle, documentFilename) {
    var link = document.createElement('a');
    link.setAttribute('download', documentFilename);

    var content = "<!DOCTYPE html>\n";
    content += "<html>\n";
    content += "<head>\n";
    content += `<title>${documentTitle}</title>\n`;
    content += "</head>\n";
    content += "<body>\n";

    content += data;

    content += "</body>\n";
    content += "</html>\n";

    link.href = makeTextFile(content);
    document.body.appendChild(link);

    // wait for the link to be added to the document
    window.requestAnimationFrame(function () {
        var event = new MouseEvent('click');
        link.dispatchEvent(event);
        window.URL.revokeObjectURL(link.href);
        document.body.removeChild(link);

    });
}


function makeTextFile(text) {
    var data = new Blob([text], {type: 'text/html'});
    return window.URL.createObjectURL(data);
};
