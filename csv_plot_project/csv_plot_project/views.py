import pandas as pd
import plotly.express as px
import io
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status
from django.http import HttpResponse

class FileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request):
        # Check if the file was uploaded
        if 'file' not in request.FILES:
            return Response({"message": "No file was submitted."}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']
        print("Received content type:", csv_file.content_type)

        
        if not csv_file.name.endswith('.csv'):
            return Response({"message": "Invalid file type. Only CSV files are accepted."}, status=status.HTTP_400_BAD_REQUEST)


        content = csv_file.read().decode('utf-8')
        print("Content to UTF8: ", content[:500])  # print first 500 characters
        # Extract the actual CSV data
        csv_content_start = content.find("\r\n\r\n") + 4  # +4 to skip the double newline itself
        csv_content = content[csv_content_start:]

        # Use StringIO to create a file-like object and read with Pandas
        csv_file_like = io.StringIO(csv_content)
        print("Extracted CSV content:", csv_content[:500])  # print first 500 characters of the extracted content

        try:
            df = pd.read_csv(csv_file_like, delimiter=',')
        except pd.errors.ParserError as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except pd.errors.EmptyDataError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



        # Plotting
        fig = px.line(df, x=df.columns[0], y=df.columns[1:])  # A line plot with the first column as x and the rest as y values
        output = io.BytesIO()
        fig.write_image(output, format='png')
        output.seek(0)

        # Return the image
        response = HttpResponse(output, content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="plot.png"'

        return response
