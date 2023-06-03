async function onSubmit(event) {
    event.preventDefault();
    const urlInput = document.getElementById('url');
    const url = urlInput.value;
    const id = extractVideoId(url);
    const button = event.target.querySelector('button');
    button.classList.add('buttonLoading');
    button.innerText = 'Please wait...';
    if (id) {
        const response = await fetch(`/mp4?id=${id}`);
        if (response.status === 202) {  // Check if status is "Accepted"
            const data = await response.json();
            checkDownloadStatus(data.download_id, button);
        } else {
            button.classList.remove('buttonLoading');
            button.innerText = 'Download';
            alert('Failed to start download');
        }
    } else {
        button.classList.remove('buttonLoading');
        button.innerText = 'Download';
        alert('Invalid YouTube URL or video ID');
    }
}
async function checkDownloadStatus(download_id, button) {
    const response = await fetch(`/download/${download_id}`);
    if (response.status === 200) {  // Check if status is "OK"
        button.classList.remove('buttonLoading');
        button.innerText = 'Download';
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${download_id}.mp4`;
        link.click();
    } else if (response.status === 202) {  // Check if status is "Accepted"
        // If the download is still processing, check again in a few seconds
        setTimeout(() => checkDownloadStatus(download_id, button), 5000);
    } else {
        button.classList.remove('buttonLoading');
        button.innerText = 'Download';
        alert('Failed to download video');
    }
}

function extractVideoId(url) {
  const regex = /(youtu\.be\/|youtube\.com\/(watch\?(.*&)?v=|(embed|v)\/))([^\?&"'>]+)/;
  const matches = url.match(regex);
  if (matches && matches.length > 5) {
      return matches[5];
  } else if (url.length == 11) { // A plain video id
      return url;
  } else {
      return null;
  }
}