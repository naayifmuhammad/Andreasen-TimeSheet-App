import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph


def generate_pdf(filename, project, timesheets, duration, total):
    # Create a response object and set content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create a PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    style_left = ParagraphStyle(
    'LeftAligned',
    parent=styles['Normal'],
    alignment=0,  # Left alignment
    fontSize=12,
    spaceAfter=6
)

    # Add company name and project name
    elements.append(Paragraph(f"{project.team}", styles['Title']))
    elements.append(Paragraph("<br/><br/><br/>",styles['Normal']))
    elements.append(Paragraph(f"Project: {project.name}({project.code})", style_left))
    elements.append(Paragraph(f"{duration['pStart']} to {duration['cEnd']}", styles['Normal']))
    elements.append(Paragraph("<br/><br/>", styles['Normal'])) 

    # Create table data
    table_data = [
        ['Employee', 'Description of Work', 'Hours Worked'],
    ]
    
    # Add data from previous and current timesheets
    for week_key in ['previous', 'current']:
        week_timesheets = timesheets[week_key]
        for timesheet in week_timesheets:
            table_data.append([
                timesheet.employee,
                timesheet.description,
                timesheet.hours_worked,
            ])

    # Create table
    table = Table(table_data,colWidths=[doc.width / 3.0] * len(table_data[0]))
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)

    elements.append(Paragraph("<br/><br/><br/>",styles['Normal']))
    elements.append(Paragraph(f"Total hours worked: {total['previous']+total['current']} hours", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
