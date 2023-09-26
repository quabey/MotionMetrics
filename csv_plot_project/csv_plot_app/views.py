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
        
        # Read CSV into DataFrame
        try:
            df = pd.read_csv(csv_file, delimiter=',')
        except FileNotFoundError:
            return Response({"message": "File not found."}, status=status.HTTP_400_BAD_REQUEST)
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
