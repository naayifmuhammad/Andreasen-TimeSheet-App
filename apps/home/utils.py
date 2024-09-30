import calendar
from decimal import Decimal
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





from collections import defaultdict
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import io
from django.http import HttpResponse

def generate_project_report(single_mode, project=None, team=None, timesheets=None, duration=None, filename=None):
    # Create a response object and set content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create a PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    # Footer style
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
        'LeftAlignedBold',
        parent=styles['Normal'],
        alignment=0,  # Left alignment
        fontSize=9,
        fontName='Helvetica-Bold',  # Bold font
        spaceAfter=6
    )

    #currently not using this single project mode. Just ensure that the report generation using checkboxes work
    if single_mode:
        # elements.append(Paragraph(f"{team}", styles['Title']))
        # elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
        # elements.append(Paragraph(f"Project: {project.name}({project.code})", style_left))
        # elements.append(Paragraph(f"Customer: {project.customer.name}", style_left))
        # elements.append(Paragraph(f"{duration['start']} to {duration['end']}", styles['Normal']))
        # elements.append(Paragraph("<br/><br/>", styles['Normal']))

        # # Create table data
        # table_data = [
        #     ['Date', 'Employee', 'Description', 'Hours Worked'],
        # ]

        # # Group the timesheets by employee and description, and sum the hours worked
        # grouped_timesheets = defaultdict(lambda: defaultdict(float))
        # for week in timesheets:
        #     for timesheet in week:
        #         key = (timesheet.employee, timesheet.description)
        #         grouped_timesheets[key][timesheet.date] += float(timesheet.hours_worked)


        # total_hours_worked = 0
        # for (employee, description), date_hours in grouped_timesheets.items():
        #     for date, hours in date_hours.items():
        #         table_data.append([
        #             date,
        #             employee,
        #             description,
        #             hours
        #         ])
        #         total_hours_worked += hours

        # table_data.append(["", "", "", ""])
        # table_data.append(["", "", Paragraph("Total:", blackTH), Paragraph(str(total_hours_worked), blackTH)])
        pass

    else:
        elements.append(Paragraph(f"{team}", styles['Title']))
        elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
        elements.append(Paragraph(f"Project Report", style_left))
        elements.append(Paragraph(f"{duration['start']} to {duration['end']}", styles['Normal']))
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

        # Create table data
        table_data = [
            ['Employee', 'Description', 'Hours Worked'],
        ]

        monthly_total = Decimal(0)  # Initialize as Decimal
        for project_info in timesheets:
            weekly_total = Decimal(0) # Initialize as Decimal
            # Add a header row for the project
            table_data.append([
                Paragraph(f"{project_info['project_code']}", blackTH),
                Paragraph(f"{project_info['project_name']}", blackTH),
                Paragraph(f"{project_info['customer_name']}", blackTH),
            ])

            # Group the timesheets by employee and description for this project
            unique_timesheets = defaultdict(Decimal)  # Only store unique employee-description combos

            for timesheet in project_info['timesheets']:
                # Create a unique key for each combination of employee and description
                key = (timesheet.employee, timesheet.description)
                unique_timesheets[key] += Decimal(timesheet.hours_worked)  # Sum hours for unique combos

            # Populate table data with unique entries
            for (employee, description), hours in unique_timesheets.items():
                table_data.append([
                    employee,
                    description,
                    hours
                ])
                weekly_total += hours
                monthly_total += hours
            
            table_data.append(["", Paragraph("Weekly Total:", blackTH), Paragraph(str(weekly_total), blackTH)])
            table_data.append(["", '',''])

        table_data.append(["", Paragraph("Monthly Total:", blackTH), Paragraph(str(monthly_total), blackTH)])

        # Create the table
        colWidths = [doc.width * 0.33, doc.width * 0.33, doc.width * 0.33]
        table = Table(table_data, colWidths=colWidths)
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

        elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
        elements.append(Paragraph(f"Total hours worked: {monthly_total} hours", style_left_bold))

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

    # Define the header and footer styles
    whiteTH = ParagraphStyle(
        'WhiteBoldText',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
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

    # Initialize the total hours for each day
    total_time_worked_in_specific_day = {
        'Monday': 0,
        'Tuesday': 0,
        'Wednesday': 0,
        'Thursday': 0,
        'Friday': 0,
        'Saturday': 0,
        'Sunday': 0,
    }
    overAllTotalTimeWorked = 0

    for weekrange in weekranges:
        weeklytotalworkdone = 0

        # Create a dictionary to hold the project and description data
        work_data = {}

        # Group timesheets by (project, description)
        for timesheet in weekrange['timesheets']:
            key = (timesheet.project.code, timesheet.description)
            if key not in work_data:
                work_data[key] = {
                    'Monday': 0,
                    'Tuesday': 0,
                    'Wednesday': 0,
                    'Thursday': 0,
                    'Friday': 0,
                    'Saturday': 0,
                    'Sunday': 0,
                    'Total': 0
                }
            # Add hours to the appropriate day
            day_of_week = timesheet.date.strftime('%A')
            work_data[key][day_of_week] += timesheet.hours_worked
            work_data[key]['Total'] += timesheet.hours_worked

            # Update the overall totals
            total_time_worked_in_specific_day[day_of_week] += timesheet.hours_worked
            overAllTotalTimeWorked += timesheet.hours_worked
            weeklytotalworkdone += timesheet.hours_worked

        # Create the table data
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

        # Add rows for each project and description from the work_data dictionary
        for (project_code, description), hours in work_data.items():
            table_data.append([
                Paragraph(project_code, styleN),
                Paragraph(description, styleN),
                Paragraph(str(hours['Monday']), styleN),
                Paragraph(str(hours['Tuesday']), styleN),
                Paragraph(str(hours['Wednesday']), styleN),
                Paragraph(str(hours['Thursday']), styleN),
                Paragraph(str(hours['Friday']), styleN),
                Paragraph(str(hours['Saturday']), styleN),
                Paragraph(str(hours['Sunday']), styleN),
                Paragraph(str(hours['Total']), styleN),
            ])

        # Add totals for the week
        table_data.append([
            Paragraph('', blackTH),
            Paragraph('Total', blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Monday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Tuesday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Wednesday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Thursday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Friday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Saturday"]), blackTH),
            Paragraph(str(total_time_worked_in_specific_day["Sunday"]), blackTH),
            Paragraph(str(weeklytotalworkdone), blackTH),
        ])

        # Column widths
        fixed_columns_width = (doc.width * 0.14) + (doc.width * 0.15) + (doc.width * 0.07)
        remaining_width = doc.width - fixed_columns_width
        day_column_width = remaining_width / 7

        col_widths = [
            doc.width * 0.14,  # 14% for 'Project'
            doc.width * 0.12,  # 15% for 'Description'
            day_column_width,  # Distributed width for 'Monday'
            day_column_width,  # Distributed width for 'Tuesday'
            day_column_width,  # Distributed width for 'Wednesday'
            day_column_width,  # Distributed width for 'Thursday'
            day_column_width,  # Distributed width for 'Friday'
            day_column_width,  # Distributed width for 'Saturday'
            day_column_width,  # Distributed width for 'Sunday'
            doc.width * 0.10   # 7% for 'Total'
        ]

        # Create and style the table
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

        # Add the table to the elements
        elements.append(table)

    # Add total hours worked at the end of the document
    elements.append(Paragraph("<br/><br/><br/>", styles['Normal']))
    elements.append(Paragraph(f"Total: {overAllTotalTimeWorked} hours", style_left))

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response



 