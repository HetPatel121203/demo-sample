from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
import os

# Set up Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey123'  # Needed for form security

# Simple form class for input
class CodeForm(FlaskForm):
    user_code = TextAreaField('Code', validators=[DataRequired()])
    change_prompt = TextAreaField('Change Request', validators=[DataRequired()])
    submit = SubmitField('Get Suggestions')

# Function to make changes to the code
def modify_code(original_code, user_prompt):
    new_code = original_code
    explanation = ''
    prompt = user_prompt.lower()  # Make it easier to check

    # Check what the user wants to do
    if 'error handling' in prompt:
        """Add try-catch to functions"""
        if 'function' in new_code:
            lines = new_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('function'):
                    lines[i] = line + '\n    try {'
                    # Find the closing brace
                    brace_count = 0
                    for j in range(i, len(lines)):
                        if '{' in lines[j]:
                            brace_count += 1
                        if '}' in lines[j]:
                            brace_count -= 1
                            if brace_count == 0:
                                lines[j] = '    } catch (err) {\n        console.log("Error caught:", err);\n    }'
                                break
            new_code = '\n'.join(lines)
            explanation = 'Added a try-catch block inside the function to handle errors. It logs any errors to the console.'
        else:
            explanation = 'No functions found to add error handling to!'
    elif 'optimize loop' in prompt or 'better loop' in prompt:
        # Convert for loop to forEach
        if 'for (let' in new_code:
            lines = new_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('for (let') and '.length' in line:
                    # Extract array name and loop body
                    array_name = line.split('<')[1].split('.length')[0].strip()
                    body_start = line.index('{') + 1
                    body_end = line.rindex('}')
                    loop_body = line[body_start:body_end].strip()
                    lines[i] = f'{array_name}.forEach(item => {{{loop_body}}});'
            new_code = '\n'.join(lines)
            explanation = 'Changed the for loop to a forEach. It’s more readable and modern.'
        else:
            explanation = 'Didn’t find any for loops to optimize.'
    elif 'logging' in prompt or 'add log' in prompt:
        # Add console.log to functions
        if 'function' in new_code:
            lines = new_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('function'):
                    lines[i] = line + '\n    console.log("Starting function...");'
            new_code = '\n'.join(lines)
            explanation = 'Added a console.log at the start of the function for debugging purposes.'
        else:
            explanation = 'No functions to add logging to.'
    else:
        explanation = 'I didn’t understand the request. Try "add error handling", "optimize loop", or "add logging".'

    return new_code, explanation

# Main route for the form
@app.route('/', methods=['GET', 'POST'])
def index():
    form = CodeForm()
    modified_code = None
    explanation = None
    final_code = None

    if form.validate_on_submit():
        user_code = form.user_code.data
        change_prompt = form.change_prompt.data

        # Double-check inputs (just to be safe)
        if not user_code or not change_prompt:
            flash('Please fill in both fields!', 'error')
        else:
            # Process the code
            modified_code, explanation = modify_code(user_code, change_prompt)

            # Check if user clicked "Apply Changes"
            if 'apply_changes' in request.form:
                final_code = modified_code
                form.user_code.data = final_code  # Update the form input

    return render_template('index.html', form=form, modified_code=modified_code,
                         explanation=explanation, final_code=final_code)

if __name__ == '__main__':
    # Use port 5001 to avoid conflicts (based on your past issues)
    app.run(debug=True, port=5001)