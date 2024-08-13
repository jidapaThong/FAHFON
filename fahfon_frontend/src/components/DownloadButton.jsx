import React from "react";

const DownloadButton = ({url, filename}) =>{
    
    const handleDownload = async () =>{
        console.log(url);
        console.log(filename);
        try{
            const response = await fetch(url);
            if (!response.ok) {
              throw new Error("File download failed");
            }
            const blob = await response.blob();
            const downloadLink = document.createElement("a");
            downloadLink.href = URL.createObjectURL(blob);
            downloadLink.download = filename;
            downloadLink.click();
        } catch (error) {console.error(error);}
    }
    
    return (
        <button onClick={handleDownload}>Download Data</button>
    );
}

export default DownloadButton