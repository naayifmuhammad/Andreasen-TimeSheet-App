import calendar
import io
from io import BytesIO

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter #type:ignore   
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph #type:ignore  
from reportlab.lib import colors #type:ignore 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle #type:ignore
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER  # type: ignore # Import alignment constants
from reportlab.platypus import Paragraph #type:ignore
from datetime import timedelta, datetime
from .models import Timesheet
from dateutil.relativedelta import relativedelta
from reportlab.lib.colors import HexColor




##########################################
#current version test date range funtion. keep if working

def get_monday_of_week(date):
    return date - timedelta(days=date.weekday())

def generate_week_ranges_from_given_startdate_till_date(start_date=None, end_date=None):
    if start_date == end_date == None:
        start_date=Timesheet.objects.earliest('date').date
        end_date = datetime.now().date()
    week_ranges = []
    start_of_week = get_monday_of_week(start_date)
    while start_of_week <= end_date:
        end_of_week = start_of_week + timedelta(days=6)
        week_ranges.append({"start": start_of_week , "end" : end_of_week})
        start_of_week += timedelta(days=7)
    return week_ranges


def getBiWeeklyRanges():
    biweekly_ranges = []
    weekranges = generate_week_ranges_from_given_startdate_till_date()
    if len(weekranges) > 1:
        for week_index in range(len(weekranges)-1):
            biweekly_ranges.append({"biweekly_start":weekranges[week_index]['start'].strftime("%d/%m/%Y"),"biweekly_end":weekranges[week_index+1]['end'].strftime("%d/%m/%Y")})
        return biweekly_ranges[::-1]
    else:
        biweekly_ranges.append({"biweekly_start":weekranges[0]['start'].strftime("%d/%m/%Y"),"biweekly_end":weekranges[0]['end'].strftime("%d/%m/%Y")})
        return biweekly_ranges[::-1]


def get_report_ready_months():
    try:
        # Get the earliest date from the Timesheet model
        earliest_date = Timesheet.objects.earliest('date').date
        # Get the current date
        end_date = datetime.now().date()

        # Initialize a list to hold the months
        months = []

        # Start from the earliest date and go up to the current date
        current_date = earliest_date
        while current_date <= end_date:
            # Get the start and end dates of the current month
            start_of_month = current_date.replace(day=1).strftime('%d/%m/%Y')
            _, last_day = calendar.monthrange(current_date.year, current_date.month)
            end_of_month = current_date.replace(day=last_day).strftime('%d/%m/%Y')

            # Append the month data to the list
            months.append({
                'month': current_date.strftime('%B %Y'),
                'month_start': start_of_month,
                'month_end': end_of_month
            })

            # Move to the next month
            current_date += relativedelta(months=1)
        return months
    except Timesheet.DoesNotExist:
        # Handle the exception when no Timesheets exist
        return None





#generates the pdf for project based report
def generate_project_report(single_mode, project=None,team=None, timesheets=None, duration=None, filename=None):
    # Create a response object and set content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    
    # Create a PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()




    # footer  style
    blackTH = ParagraphStyle(
        'blackBoldText',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',  # Bold font
        fontSize=9,
        textColor=colors.black,
        splitLongWords=True,
    )


    style_left = ParagraphStyle(
    'LeftAligned',
    parent=styles['Normal'],
    alignment=0,  # Left alignment
    fontSize=12,
    spaceAfter=6
)
    style_left_bold = ParagraphStyle(
    'LeftAligned',
    parent=styles['Normal'],
    alignment=0,  # Left alignment
    fontSize=9,
    fontName='Helvetica-Bold',  # Bold font
    spaceAfter=6
)


    if single_mode:
        
        elements.append(Paragraph(f"{team}", styles['Title']))
        elements.append(Paragraph("<br/><br/><br/>",styles['Normal']))
        elements.append(Paragraph(f"Project: {project.name}({project.code})", style_left))
        elements.append(Paragraph(f"Customer: {project.customer.name}", style_left))
        elements.append(Paragraph(f"{duration['start']} to {duration['end']}", styles['Normal']))
        elements.append(Paragraph("<br/><br/>", styles['Normal'])) 

        # Create table data
        table_data = [
            ['Date','Employee', 'Description', 'Hours Worked'],
        ]

        # Add data from previous and current timesheets
        total_hours_worked = 0
        for week in timesheets:
            for timesheet in week:
                table_data.append([
                    timesheet.date,
                    timesheet.employee,
                    timesheet.description,
                    timesheet.hours_worked,
                ])
                total_hours_worked += timesheet.hours_worked
        table_data.append(["","","",""])
        table_data.append(["","",Paragraph("Total:",blackTH),Paragraph(total_hours_worked,blackTH)])
    
    else:
        
        elements.append(Paragraph(f"{team}", styles['Title']))
        elements.append(Paragraph("<br/><br/><br/>",styles['Normal']))
        elements.append(Paragraph(f"Project Report", style_left))
        elements.append(Paragraph(f"{duration['start']} to {duration['end']}", styles['Normal']))
        elements.append(Paragraph("<br/><br/>", styles['Normal'])) 

        # Create table data
        table_data = [
            ['Date','Employee', 'Description', 'Hours Worked'],
        ]
        total_hours_worked = 0
        for project_info in timesheets:
            # Add a header row for the project
            table_data.append([
                Paragraph(f"{project_info['project_code']}",blackTH),
                Paragraph(f"{project_info['project_name']}",blackTH),
                Paragraph(f"{project_info['customer_name']}",blackTH),
                '',
            ])
            total_for_this_project  = 0
            for timesheet in project_info['timesheets']:
                table_data.append([
                    timesheet.date,
                    timesheet.employee,
                    timesheet.description,
                    timesheet.hours_worked,
                ])
                total_hours_worked += timesheet.hours_worked
                total_for_this_project+=timesheet.hours_worked

            # Add a blank row for spacing
            table_data.append(["","",Paragraph("Total:",blackTH),Paragraph(str(total_for_this_project),blackTH)])
            table_data.append(["","","",""])
        table_data.append(["", "", Paragraph("Monthly Total:",blackTH),Paragraph(str(total_hours_worked),blackTH)])

    # Create table
    colWidths = [doc.width * 0.25,doc.width * 0.2,doc.width * 0.4,doc.width * 0.15]
    table = Table(table_data,colWidths=colWidths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#088484")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    
    elements.append(table)

    elements.append(Paragraph("<br/><br/><br/>",styles['Normal']))
    elements.append(Paragraph(f"Total hours worked: {total_hours_worked} hours", style_left_bold))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response



#new function biweekly split into 2 tables follows desc based dictionary structure from index view::
def generate_employee_report(employee, weekranges, filename, duration):
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
    styleN.fontSize = 9
    styleN.alignment = TA_LEFT
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER

    # Define the header style
    whiteTH = ParagraphStyle(
        'WhiteBoldText',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )

    # Footer style
    blackTH = ParagraphStyle(
        'blackBoldText',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.black
    )

    style_left = ParagraphStyle(
        'LeftAligned',
        parent=styles['Normal'],
        alignment=0,
        fontName='Helvetica-Bold',
        fontSize=11,
        spaceAfter=6
    )

    # Add company name and project name
    elements.append(Paragraph(f"{employee.get_full_name()}", styles['Title']))
    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
    elements.append(Paragraph(f"Team: {employee.team.name}", style_left))
    elements.append(Paragraph(f"{duration['start'].strftime('%d-%m-%y')} to {duration['end'].strftime('%d-%m-%y')}", style_left))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Initialize total work time
    total_time_worked_in_specific_day = {
        'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0,
        'Saturday': 0, 'Sunday': 0
    }
    overAllTotalTimeWorked = 0

    # Loop through weekranges
    for weekrange in weekranges:
        weeklytotalworkdone = 0

        # Create table data with updated headers for Saturday and Sunday
        table_data = [
            [
                'Project', 'Description',
                Paragraph(f"Mon<br/>{weekrange['dates'][0]}", whiteTH), 
                Paragraph(f"Tue<br/>{weekrange['dates'][1]}", whiteTH), 
                Paragraph(f"Wed<br/>{weekrange['dates'][2]}", whiteTH), 
                Paragraph(f"Thu<br/>{weekrange['dates'][3]}", whiteTH), 
                Paragraph(f"Fri<br/>{weekrange['dates'][4]}", whiteTH),
                Paragraph(f"Sat<br/>{weekrange['dates'][5]}", whiteTH),
                Paragraph(f"Sun<br/>{weekrange['dates'][6]}", whiteTH),
                'Total'
            ]
        ]

        # Add timesheet data to the table
        for timesheet in weekrange['timesheets']:
            day = timesheet.date.strftime('%A')
            total_time_worked_in_specific_day[day] += timesheet.hours_worked
            overAllTotalTimeWorked += timesheet.hours_worked
            weeklytotalworkdone += timesheet.hours_worked

            table_data.append([
                Paragraph(timesheet.project.code, styleN),
                Paragraph(timesheet.description, styleN),  # Wrapping text in Paragraph
                Paragraph(str(0 if day != 'Monday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if day != 'Tuesday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if day != 'Wednesday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if day != 'Thursday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if day != 'Friday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if day != 'Saturday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if day != 'Sunday' else timesheet.hours_worked), styleN),
                Paragraph(str(timesheet.hours_worked), styleN),
            ])

        # Add weekly total row
        table_data.append([
            Paragraph('', blackTH),
            Paragraph('Total hours worked', blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Monday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Tuesday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Wednesday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Thursday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Friday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Saturday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Sunday"]), blackTH),
            Paragraph(str(weeklytotalworkdone), blackTH),
        ])

        # Define column widths
        col_widths = [
            doc.width * 0.12,  # Project column
            doc.width * 0.24,  # Description column
            doc.width * 0.08,  # Monday column
            doc.width * 0.08,  # Tuesday column
            doc.width * 0.08,  # Wednesday column
            doc.width * 0.08,  # Thursday column
            doc.width * 0.08,  # Friday column
            doc.width * 0.08,  # Saturday column
            doc.width * 0.08,  # Sunday column
            doc.width * 0.08   # Total column
        ]

        # Create and style the table
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#088484')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),  # Font size set to 9
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))

        # Add the table to the elements
        elements.append(table)

    # Add overall total work hours at the end
    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
    elements.append(Paragraph(f"Total: {overAllTotalTimeWorked} hours", style_left))

    # Build PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response






# Function to generate employee report PDF {old code, uncomment if the newer one fails to work}
def generate_employee_report(employee, weekranges, filename, duration):
    # Create a response object and set content type
    print(weekranges)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
  
    # Create a PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    # Define styles
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontSize = 9
    styleN.alignment = TA_LEFT
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    # Define the header style
    whiteTH = ParagraphStyle(
        'WhiteBoldText',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',  # Bold font
        fontSize=9,
        textColor=colors.white
    )
    # footer  style
    blackTH = ParagraphStyle(
        'blackBoldText',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',  # Bold font
        fontSize=9,
        textColor=colors.black
    )
    style_left = ParagraphStyle(
        'LeftAligned',
        parent=styles['Normal'],
        alignment=0,  # Left alignment
        fontName='Helvetica-Bold',  # Bold font
        fontSize=11,
        spaceAfter=6
    )
    # Add company name and project name
    elements.append(Paragraph(f"{employee.get_full_name()}", styles['Title']))
    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
    elements.append(Paragraph(f"Team: {employee.team.name}", style_left))
    elements.append(Paragraph(f"{duration['start'].strftime('%d-%m-%y')} to {duration['end'].strftime('%d-%m-%y')}", style_left))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))
  
  
    # Add data from previous and current timesheets
    total_time_worked_in_specific_day = {
        'Monday' : 0,
        'Tuesday' : 0,
        'Wednesday' : 0,
        'Thursday' : 0,
        'Friday' : 0,
        'Saturday' : 0,
        'Sunday' : 0,
    }
    overAllTotalTimeWorked = 0
    for weekrange in weekranges:
        weeklytotalworkdone = 0
        # Create table data
        table_data = [
            [
        'Project', 'Description',
        Paragraph(f"Mon<br/>{weekrange['dates'][0]}",whiteTH), Paragraph(f"Tue<br/>{weekrange['dates'][1]}",whiteTH), 
        Paragraph(f"Wed<br/>{weekrange['dates'][2]}",whiteTH), Paragraph(f"Thu<br/>{weekrange['dates'][3]}",whiteTH), 
        Paragraph(f"Fri<br/>{weekrange['dates'][4]}",whiteTH), 
        Paragraph(f"Sat<br/>{weekrange['dates'][5]}",whiteTH), 
        Paragraph(f"Sun<br/>{weekrange['dates'][6]}",whiteTH), 'Total'
            ]
        ]
        for timesheet in weekrange['timesheets']:
            total_time_worked_in_specific_day[timesheet.date.strftime('%A')] += timesheet.hours_worked
            overAllTotalTimeWorked += timesheet.hours_worked
            weeklytotalworkdone += timesheet.hours_worked
            table_data.append([
                Paragraph(timesheet.project.code, styleN),
                Paragraph(timesheet.description, styleN),  # Wrapping text in Paragraph
                Paragraph(str(0 if timesheet.date.strftime('%A') != 'Monday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if timesheet.date.strftime('%A') != 'Tuesday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if timesheet.date.strftime('%A') != 'Wednesday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if timesheet.date.strftime('%A') != 'Thursday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if timesheet.date.strftime('%A') != 'Friday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if timesheet.date.strftime('%A') != 'Saturday' else timesheet.hours_worked), styleN),
                Paragraph(str(0 if timesheet.date.strftime('%A') != 'Sunday' else timesheet.hours_worked), styleN),
                Paragraph(str(timesheet.hours_worked), styleN),
            ])
     
        table_data.append([
            Paragraph('', blackTH),
            Paragraph('Total hours worked', blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Monday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Tuesday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Wednesday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Thursday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Friday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Saturday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Sunday"]), blackTH),
            Paragraph(str(weeklytotalworkdone), blackTH),
        ])
        # Fixed column widths for 'Project', 'Description', and 'Total'
        fixed_columns_width = (doc.width * 0.14) + (doc.width * 0.15) + (doc.width * 0.07)
        
        # Remaining width to be distributed among the 7 day columns (Monday to Sunday)
        remaining_width = doc.width - fixed_columns_width
        
        # Evenly distribute the remaining width among the 7 day columns
        day_column_width = remaining_width / 7
        
        col_widths = [
            doc.width * 0.14,  # 14% for 'Project'
            doc.width * 0.15,  # 15% for 'Description'
            day_column_width,  # Distributed width for 'Monday'
            day_column_width,  # Distributed width for 'Tuesday'
            day_column_width,  # Distributed width for 'Wednesday'
            day_column_width,  # Distributed width for 'Thursday'
            day_column_width,  # Distributed width for 'Friday'
            day_column_width,  # Distributed width for 'Saturday'
            day_column_width,  # Distributed width for 'Sunday'
            doc.width * 0.07   # 7% for 'Total'
        ]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#088484')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),  # Set font size to 9 points
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        elements.append(table)
    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
    elements.append(Paragraph(f"Total: {overAllTotalTimeWorked} hours", style_left))
  
    # Build PDF
    doc.build(elements)
  
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
  
    return response


 