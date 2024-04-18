import os
import sys

from app.models.models import Text, Summary
from app.summarizer.text_summarizer import TextSummarizer
from app.utils.helpers import allowed_file, read_text_from_file, get_or_generate_percentage
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from werkzeug.utils import secure_filename

bp = Blueprint('routes', __name__, url_prefix='/api/v1')


@bp.route('/', methods=['GET'])
@bp.route('/home', methods=['GET'])
@cross_origin()
def home():
    """
    Endpoint to check if the server is running.

    Returns:
        JSON response indicating that the server is running.
    """
    return jsonify({"message": "Server is running"})


@bp.route('/texts', methods=['GET'])
@cross_origin()
def get_all_texts():
    """
    Endpoint to retrieve all texts.

    Returns:
        JSON response containing a list of all texts with first 20 characters.
    """
    texts = Text.objects.all()
    texts_data = [
        {
            'id': str(text.id),
            'text': text.content[:20] + '...' if len(text.content) > 20 else text.content,
        }
        for text in texts
    ]
    return jsonify(texts_data)


@bp.route('/text/summary/<text_id>', methods=['GET'])
@cross_origin()
def get_text_by_id(text_id):
    """
    Endpoint to retrieve a text by its ID.

    Args:
        text_id: The ID of the text to retrieve.

    Returns:
        JSON response containing the text with the specified ID.
    """
    text = Text.get_text_by_id(text_id)
    if text:
        return jsonify({
            'id': str(text.id),
            'text': text.content,
            'user_uid': text.user_uid,
            'uploaded_filename': text.uploaded_filename,
            'percentage': text.percentage,
            'created_at': text.created_at.isoformat(),
            'summaries': [
                {
                    'id': str(summary.id),
                    'text': summary.content,
                    'created_at': summary.created_at.isoformat(),
                    'percentage': summary.percentage,
                    'words': summary.words
                } for summary in text.summaries
            ]
        })
    else:
        return jsonify({"error": "Text not found"}), 404


@bp.route('/texts/user/', methods=['GET'])
@cross_origin()
def get_user_texts_and_summaries():
    """
    Endpoint to retrieve all texts and their associated summaries for the user.

    Returns:
        JSON response containing a list of texts and their summaries for the user.
    """
    user_uid = request.headers.get('X-User-UID')
    if not user_uid:
        return jsonify({"error": "X-User-UID header is missing"}), 400

    # Fetch all texts for the user
    user_texts = Text.get_texts_by_user(user_uid)

    if not user_texts:
        return jsonify({"error": "No texts found for the user"}), 404

    # sys.stdout.write(f'${user_uid} has {len(user_texts)} texts\n')

    texts_data = [
        {
            'id': str(text.id),
            'title': text.content[:50] + '...' if len(text.content) > 50 else text.content,
            'created_at': text.created_at.isoformat(),
        }
        for text in user_texts
    ]

    # Construct and return the JSON response
    return jsonify(texts_data)


@bp.route('/texts-summaries', methods=['GET'])
@cross_origin()
def get_texts_summaries():
    """
    Endpoint to retrieve all texts along with their summaries.

    Returns:
        JSON response containing a list of texts and their summaries.
    """
    texts = Text.objects.all()

    texts_data = [
        {
            'id': str(text.id),
            'text': text.content,
            'user_uid': text.user_uid,
            'created_at': text.created_at.isoformat(),
            'summaries': [
                {
                    'id': str(summary.id),
                    'text': summary.content,
                    'created_at': summary.created_at.isoformat(),
                    'percentage': summary.percentage,
                    'words': summary.words
                }
                for summary in text.summaries
            ]
        }
        for text in texts
    ]
    return jsonify(texts_data)


@bp.route('/texts/<text_id>/summaries', methods=['GET'])
@cross_origin()
def get_text_summaries(text_id):
    """
    Endpoint to retrieve a text and its associated summaries by ID.

    Parameters:
        text_id (str): The ID of the text to be retrieved.

    Returns:
        JSON response containing the text and its summaries.
    """
    text = Text.get_text_with_summaries(text_id)
    text_summaries = [{
        'id': str(summary.id),
        'text': summary.content,
        'created_at': summary.created_at.isoformat(),
        'percentage': summary.percentage,
        'words': summary.words
    } for summary in text.summaries]
    if text:
        return jsonify({
            'id': str(text.id),
            'text': text.content,
            'summaries': text_summaries
        })
    else:
        return jsonify({"error": "Text not found"}), 404


@bp.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    """
    Endpoint to handle file uploads.

    Returns:
        JSON response indicating the success or failure of the file upload,
        and the extracted text content from the uploaded file.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "No selected file or file type not allowed"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    # Save the file to the uploads folder
    file.save(filepath)

    # Read the text from the file
    text_content = read_text_from_file(filepath).replace('\n', ' ')

    # Create a new Text document and save it to the database
    user_uid = request.headers.get('X-User-UID')
    percentage = get_or_generate_percentage(int(request.form.get('percentage')))
    text = Text.create_text(content=text_content, user_uid=user_uid, uploaded_filename=filename, percentage=percentage)

    # Use the TextSummarizer to summarize the fetched text
    summarizer = TextSummarizer(text.content, percentage, 8)
    summary = summarizer.summarize()
    words = len(summary.split())

    # Save the summary to the database, linked to the original text
    new_summary = Summary.create_summary(
        content=summary,
        text=text,
        percentage=percentage,
        words=words
    )

    # Add the summary to the original text's list of summaries
    text.add_summary(new_summary)

    # Delete the file from the uploads folder
    os.remove(filepath)

    return jsonify({
        "message": "File uploaded successfully",
        "id": str(text.id)
    }), 201


@bp.route('/summarize', methods=['POST'], endpoint='summarize')
@cross_origin()
def summarize():
    """
    Endpoint to summarize a text.

    Returns:
        JSON response of the text id
    """
    user_uid = request.headers.get('X-User-UID')
    data = request.get_json()  # Get data as JSON
    text_content = data.get('text')
    # get or generate percentage
    percentage = get_or_generate_percentage(data.get('percentage', None))

    if not text_content:
        return jsonify({"error": "No text provided"}), 400

    # Create a new Text document and save it to the database
    text = Text.create_text(content=text_content, user_uid=user_uid, percentage=percentage)

    # Use the TextSummarizer to summarize the fetched text
    summarizer = TextSummarizer(text.content, percentage, 8)
    summary = summarizer.summarize()
    words = len(summary.split())

    # Save the summary to the database, linked to the original text
    new_summary = Summary.create_summary(
        content=summary,
        text=text,
        percentage=percentage,
        words=words
    )

    # Add the summary to the original text's list of summaries
    text.add_summary(new_summary)

    return jsonify({
        "message": "Text summarized successfully",
        "id": str(text.id)
    }), 201


@bp.route('/summarize-again/<text_id>', methods=['POST'], endpoint='summarize_again')
@cross_origin()
def summarize(text_id):
    """
    Endpoint to summarize a text with a given ID again.

    Parameters:
        text_id (str): The ID of the text to be summarized again.

    Returns:
        JSON response containing the generated summary.
    """
    data = request.get_json()

    # Fetch the original text using the provided text ID
    original_text = Text.get_text_by_id(text_id)
    if not original_text:
        return jsonify({"error": "Text not found"}), 404

    if data.get('percentage'):
        percentage = data.get('percentage')
    else:
        percentage = get_or_generate_percentage(data.get('percentage'))

    # Use the TextSummarizer to summarize the fetched text
    summarizer = TextSummarizer(original_text.content, percentage, 8)
    summary = summarizer.summarize()
    words = len(summary.split())

    # Save the summary to the database, linked to the original text
    summary = Summary.create_summary(content=summary, percentage=percentage, words=words, text=original_text)

    # Add the summary to the original text's list of summaries
    original_text.add_summary(summary)

    # Return the summary as a JSON response
    return jsonify({
        "summary": {
            "id": str(summary.id),
            "text": summary.content,
            "created_at": summary.created_at.isoformat(),
            "percentage": summary.percentage,
            "words": summary.words
        }
    })
