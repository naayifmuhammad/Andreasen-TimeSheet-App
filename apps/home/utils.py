import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter #type:ignore   
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph #type:ignore  
from reportlab.lib import colors #type:ignore 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle #type:ignore
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER  # type: ignore # Import alignment constants
from reportlab.platypus import Paragraph #type:ignore
from datetime import timedelta, datetime
from .models import Timesheet


##########################################
#current version test date range funtion. keep if working

def get_monday_of_week(date):
    return date - timedelta(days=date.weekday())

def generate_week_ranges_from_given_startdate_till_date(start_date=Timesheet.objects.earliest('date').date,end_date = datetime.now().date()):
    week_ranges = []
    start_of_week = get_monday_of_week(start_date)
    while start_of_week <= end_date:
        end_of_week = start_of_week + timedelta(days=4)
        week_ranges.append({"start": start_of_week , "end" : end_of_week})
        start_of_week += timedelta(days=7)
    return week_ranges

def getBiWeeklyRanges():
    biweekly_ranges = []
    weekranges = generate_week_ranges_from_given_startdate_till_date()
    for week_index in range(len(weekranges)-1):
        biweekly_ranges.append({"biweekly_start":weekranges[week_index]['start'].strftime("%d/%m/%Y"),"biweekly_end":weekranges[week_index+1]['end'].strftime("%d/%m/%Y")})
    return biweekly_ranges[::-1]


#generates the pdf for project based report
def generate_project_report(filename, project, timesheets, duration, total):
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
        ['Date','Employee', 'Description of Work', 'Hours Worked'],
    ]
    
    # Add data from previous and current timesheets
    for week_key in ['previous', 'current']:
        week_timesheets = timesheets[week_key]
        for timesheet in week_timesheets:
            table_data.append([
                timesheet.date.strftime('%d-%m-%Y'),
                timesheet.employee,
                timesheet.description,
                timesheet.hours_worked,
            ])

    # Create table
    table = Table(table_data,colWidths=[doc.width / 4.0] * len(table_data[0]))
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    
    elements.append(table)

    elements.append(Paragraph("<br/><br/><br/>",styles['Normal']))
    elements.append(Paragraph(f"Total hours worked: {total['previous'] + total['current']} hours", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

#creates the employee report pdf
def generate_employee_report(employee,timesheets, filename, duration):
    print("working till now")
    
#     # Create a response object and set content type
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
#     # Create a PDF object
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     elements = []

#     # Define styles
#     styles = getSampleStyleSheet()

#     style_left = ParagraphStyle(
#     'LeftAligned',
#     parent=styles['Normal'],
#     alignment=0,  # Left alignment
#     fontSize=12,
#     spaceAfter=6
# )

#     # Add company name and project name
#     elements.append(Paragraph(f"{project.team}", styles['Title']))
#     elements.append(Paragraph("<br/><br/><br/>",styles['Normal']))
#     elements.append(Paragraph(f"Project: {project.name}({project.code})", style_left))
#     elements.append(Paragraph(f"{duration['pStart']} to {duration['cEnd']}", styles['Normal']))
#     elements.append(Paragraph("<br/><br/>", styles['Normal'])) 

#     # Create table data
#     table_data = [
#         ['Date','Employee', 'Description of Work', 'Hours Worked'],
#     ]
    
#     # Add data from previous and current timesheets
#     for week_key in ['previous', 'current']:
#         week_timesheets = timesheets[week_key]
#         for timesheet in week_timesheets:
#             table_data.append([
#                 timesheet.date.strftime('%d-%m-%Y'),
#                 timesheet.employee,
#                 timesheet.description,
#                 timesheet.hours_worked,
#             ])

#     # Create table
#     table = Table(table_data,colWidths=[doc.width / 4.0] * len(table_data[0]))
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#         ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
#     ]))
    
#     elements.append(table)

#     elements.append(Paragraph("<br/><br/><br/>",styles['Normal']))
#     elements.append(Paragraph(f"Total hours worked: {total['previous'] + total['current']} hours", styles['Normal']))
    
#     # Build PDF
#     doc.build(elements)
    
#     # Get the value of the BytesIO buffer and write it to the response
#     pdf = buffer.getvalue()
#     buffer.close()
#     response.write(pdf)
    
#     return response


# Function to generate employee report PDF
def generate_employee_report(employee, timesheets, filename, duration, total):
    # Create a response object and set content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create a PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.alignment = TA_LEFT
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER

    style_left = ParagraphStyle(
        'LeftAligned',
        parent=styles['Normal'],
        alignment=0,  # Left alignment
        fontSize=12,
        spaceAfter=6
    )

    # Add company name and project name
    elements.append(Paragraph(f"{employee}", styles['Title']))
    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
    elements.append(Paragraph(f"Team: {employee.team.name}", style_left))
    elements.append(Paragraph(f"{duration['start']} to {duration['end']}", style_left))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Create table data
    table_data = [
        [Paragraph('<b>Project</b>', styleBH), Paragraph('<b>Description</b>', styleBH),
         Paragraph('<b>Mon</b>', styleBH), Paragraph('<b>Tue</b>', styleBH), Paragraph('<b>Wed</b>', styleBH),
         Paragraph('<b>Thu</b>', styleBH), Paragraph('<b>Fri</b>', styleBH)]
    ]
    
    # Add data from previous and current timesheets
    for weeks in timesheets:
        for week in weeks:
            for timesheet in week:
                table_data.append([
                    Paragraph(timesheet.project.code, styleN),
                    Paragraph(timesheet.description, styleN),  # Wrapping text in Paragraph
                    Paragraph(str(0 if timesheet.date.strftime('%A') != 'Monday' else timesheet.hours_worked), styleN),
                    Paragraph(str(0 if timesheet.date.strftime('%A') != 'Tuesday' else timesheet.hours_worked), styleN),
                    Paragraph(str(0 if timesheet.date.strftime('%A') != 'Wednesday' else timesheet.hours_worked), styleN),
                    Paragraph(str(0 if timesheet.date.strftime('%A') != 'Thursday' else timesheet.hours_worked), styleN),
                    Paragraph(str(0 if timesheet.date.strftime('%A') != 'Friday' else timesheet.hours_worked), styleN),
                ])

    # Create table with custom column widths
    col_widths = [doc.width * 0.1, doc.width * 0.45, doc.width * 0.09, doc.width * 0.09, doc.width * 0.09, doc.width * 0.09, doc.width * 0.09]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    
    elements.append(table)

    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
    elements.append(Paragraph(f"Total hours worked: {total} hours", style_left))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


 