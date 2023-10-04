import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status
from django.http import HttpResponse

class Schrittzähler:
    def __init__(self, schwellenwert=10.0):
        self.schwellenwert = schwellenwert
        self.schrittzahl = 0
        self.schritterkennung = []  # Liste für Schritterkennung hinzugefügt

    def add_data(self, dataframe):
        # Schritterkennung basierend auf dem Schwellenwert
        self.detect_steps(dataframe['Absolute acceleration (m/s^2)'])

    def detect_steps(self, total_acceleration):
        # Schritterkennung basierend auf dem Schwellenwert
        for i in range(1, len(total_acceleration)):
            if total_acceleration[i] > self.schwellenwert and total_acceleration[i - 1] <= self.schwellenwert:
                self.schrittzahl += 1
                self.schritterkennung.append(i)  # Index der Schritterkennung hinzugefügt


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


        schrittzähler = Schrittzähler(schwellenwert=1.5)  # Sie können den Schwellenwert anpassen
        schrittzähler.add_data(df)
        
        time = df['Time (s)']

        # Beschleunigungskomponenten
        acceleration_x = df['Linear Acceleration x (m/s^2)']
        acceleration_y = df['Linear Acceleration y (m/s^2)']
        acceleration_z = df['Linear Acceleration z (m/s^2)']
        # Absolute Beschleunigung
        absolute_acceleration = df['Absolute acceleration (m/s^2)']
        # Plotting
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time, y=acceleration_x, mode='lines', name='Beschleunigung X'))
        fig.add_trace(go.Scatter(x=time, y=acceleration_y, mode='lines', name='Beschleunigung Y'))
        fig.add_trace(go.Scatter(x=time, y=acceleration_z, mode='lines', name='Beschleunigung Z'))
        fig.add_trace(go.Scatter(x=time, y=absolute_acceleration, mode='lines', name='Absolute Beschleunigung'))
        fig.update_layout(
            title='Beschleunigungsdaten über die Zeit (Schrittzahl: ' + str(schrittzähler.schrittzahl) + ')',
            xaxis_title='Zeit (s)',
            xaxis_tickformat='s',
            yaxis_title='Beschleunigung (m/s^2)',
            )
        output = io.BytesIO()
        fig.write_image(output, format='svg', width=1800, height=950)
        output.seek(0)

        # Return the image
        response = HttpResponse(output, content_type='image/svg')
        response['Content-Disposition'] = 'attachment; filename="plot.svg"'

        return response
