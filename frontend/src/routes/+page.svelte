<script>
	import axios from 'axios'; // import axios
	import { toast } from 'svelte-french-toast'; // import toast

	const API_URL = 'http://127.0.0.1:8000/plot-csv/'; // Define the API URL

	let file;
	let image; // Reactive variable to hold the image URL
	let loading = false;

	async function postCSVAndShow() {
		loading = true;
		try {
			const form = new FormData();
			form.append('file', file[0]); // Append the file to the form data

			console.log(form);
			console.log(file[0]);

			const response = await axios.post(API_URL, form, {
				headers: {
					'Content-Disposition': `attachment; filename="RawData.csv"`
				},
				responseType: 'arraybuffer' // to handle binary response
			});

			if (response.status === 200) {
				// Convert the ArrayBuffer to a data URL and set it as the image src
				console.log(response);
				const blob = new Blob([response.data], { type: 'image/svg+xml' });
				image = URL.createObjectURL(blob);
			} else {
				console.error(`Error: ${response.status} - ${response.statusText}`);
			}
		} catch (error) {
			console.error('Error posting CSV:', error.message);
			toast.error('Error generating plot!', {position: "top-right"}); // Show a toast
		} finally {
			loading = false;
			toast.success('Plot generated successfully!', {position: "top-right"}); // Show a toast
		}
	}
</script>

<label for="upload">Upload a picture:</label>
<input
	accept="text/csv"
	bind:files={file}
	id="upload"
	name="avatar"
	type="file"
	on:change={postCSVAndShow}
/>

{#if !loading}
	<img src={image} alt="Generated Plot" />
{:else}
	<p>Loading...</p>
{/if}


