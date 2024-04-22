# Email Automator

The Email Automator is a Python program designed to automate the process of sending personalized emails to multiple recipients. It provides a flexible and customizable solution for various email automation needs.

## Features

- **Environment Variable Loading**: Easily configure email settings and parameters using environment variables.
- **Logging**: Comprehensive logging for tracking actions, errors, and warnings throughout the email sending process.
- **Email Sending Process**: Core functionality to send emails to recipients listed in a CSV file.
- **Email Templating**: Supports dynamic templating for email subjects and bodies using separate files.
- **Attachment Support**: Include attachments with outgoing emails.
- **Domain Blacklisting**: Skip sending emails to blacklisted domains to ensure compliance and reputation management.
- **Domain Email Count Tracking**: Track the number of emails sent to each domain to prevent exceeding daily limits.
- **Email Send Status Tracking**: Record the status of each sent email, including timestamps, delivery status, and error messages.
- **Error Handling and Retry Mechanism**: Handle email delivery failures gracefully and implement a retry mechanism with customizable wait time.
- **Enhanced Logging**: Detailed logging for each step of the email sending process, including custom log formats and class names.
- **Customizable Logging Format**: Customize logging formats according to preferences for better organization and readability.
- **Readme Documentation**: Comprehensive documentation with setup instructions, usage examples, and troubleshooting tips.

## Usage

1. **Setup Environment Variables**: Create a `.env` file and configure the following environment variables:

   - `SENDER_EMAIL`: Sender email address.
   - `SENDER_PASSWORD`: Sender email password.
   - `RECIPIENTS_FILE_PATH`: Path to the CSV file containing recipient information.
   - `EMAIL_SUBJECT_FILE`: Path to the file containing the email subject template.
   - `EMAIL_BODY_FILE`: Path to the file containing the email body template.
   - `ATTACHMENT_PATH`: Path to the attachment file (optional).
   - `DOMAIN_LIMIT`: Daily limit for sending emails to a single domain (optional).

2. **Install Dependencies**: Install required dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Program**: Execute the `EmailAutoMainExecutor.py` file to start the email sending process:

   ```bash
   python EmailAutoMainExecutor.py
   ```

4. **Monitor Logs**: Check the logs generated during the email sending process for status updates, errors, and warnings.

## Example

Below is an example of how to structure the `.env` file:

```plaintext
SENDER_EMAIL=your_email@example.com
SENDER_PASSWORD=your_email_password
RECIPIENTS_FILE_PATH=recipients.csv
EMAIL_SUBJECT_FILE=email_subject.txt
EMAIL_BODY_FILE=email_body.txt
ATTACHMENT_PATH=attachment.pdf
DOMAIN_LIMIT=5
```

## Dependencies

- `python-dotenv`: For loading environment variables from the `.env` file.
- `tabulate`: For formatting error messages in tabular form.
- `smtplib`: For sending emails using the SMTP protocol.
- `email`: For constructing email messages and attachments.
- `datetime`: For generating timestamps and date formatting.
- `csv`: For reading and writing CSV files.
- `os`: For interacting with the operating system.
- `logging`: For logging actions, errors, and warnings.

## Future Enhancements

- **Email Scheduler**: Implement a scheduler to send emails at specific times or intervals.
- **Email Template Editor**: Develop a GUI tool for designing and editing email templates.
- **Integration with CRM Systems**: Integrate with CRM systems to fetch recipient data directly.
- **Advanced Error Handling**: Enhance error handling mechanisms to provide more detailed feedback and suggestions for troubleshooting.
- **Multi-threading Support**: Add support for multi-threading to improve email sending performance for large recipient lists.
- **Interactive CLI**: Create an interactive command-line interface for easier configuration and monitoring of the email sending process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Feel free to contribute or suggest additional features!