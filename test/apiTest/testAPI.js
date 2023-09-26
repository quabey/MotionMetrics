const axios = require("axios");
const fs = require("fs");
const FormData = require("form-data");

const API_URL = "http://127.0.0.1:8000/plot-csv/";
const CSV_PATH = "./RawData.csv"; 
const OUTPUT_IMAGE_PATH = "./output.png";

async function postCSVAndDownloadImage() {
  try {
    const form = new FormData();
    form.append("file", fs.createReadStream(CSV_PATH), {
      filename: "RawData.csv",
      contentType: "text/csv", // Explicitly specify the content type
    });



    const response = await axios.post(API_URL, form, {
      headers: {
        ...form.getHeaders(),
        "Content-Disposition": `attachment; filename="RawData.csv"`,
      },
      responseType: "arraybuffer", // to handle binary response
    });

    if (response.status === 200) {
      fs.writeFileSync(OUTPUT_IMAGE_PATH, response.data);
      console.log(`Image saved to: ${OUTPUT_IMAGE_PATH}`);
    } else {
      console.error(`Error: ${response.status} - ${response.statusText}`);
    }
  } catch (error) {
    console.error("Error posting CSV:", error.message);
    if (error.response && error.response.data) {
      // Print out the server's response
      console.error(
        "Error details:",
        Buffer.from(error.response.data).toString()
      );
    }
    if (error.response && error.response.data) {
      // Write the server's response to an error file
      fs.writeFileSync(
        "errorOutput.html",
        Buffer.from(error.response.data).toString()
      );
      console.error("Error details saved to errorOutput.html");
    }
  }
}

postCSVAndDownloadImage();
