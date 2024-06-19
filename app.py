from flask import Flask, request, jsonify
from pymongo import MongoClient,errors

app = Flask(__name__)

# Set up MongoDB connection
try:
    client = MongoClient("mongodb://appuser:Kiujn7KijLo9ki@3.109.135.54:27017/innerscore?replicaSet=devrs&directConnection=true&authSource=admin")
    db = client["innerscore"]
    collection = db["ai-assist-prompts-test"]
    collection_original = db["ai-assist-prompts-rishabh-revert"]
    functional_collection = db["ai-assist-functional-prompts-rishabh"]
    functional_collection_original = db["ai-assist-functional-prompts-rishabh-revert"]
    answer_agent_collection = db["ai-assist-answer-agent-prompts-rishabh"]
    answer_agent_collection_original = db["ai-assist-answer-agent-prompts-rishabh-revert"]
    print("Connected to MongoDB")
except errors.ConnectionError as e:
    print(f"Error connecting to MongoDB: {e}")
    
def build_query(args):
    return {
        'grade': args.get('grade'),
        'interaction': args.get('interaction'),
        'learning_method': args.get('learning_method'),
        'subject': args.get('subject'),
        'topic': args.get('topic')
    }
    
# Get functional prompt
@app.route('/get_functional_prompt', methods=['GET'])
def get_functional_prompt():
    try:
        
        type= request.args.get('type')

        query = {
            'type': type
        }

        document = functional_collection.find_one(query)
        if document:
            return jsonify({'prompt': document['prompt']})
        else:
            return jsonify({'error': 'Prompt not found'+query}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Get functional base set
@app.route('/get_functional_base', methods=['GET'])
def get_functional_base():
    try:
        
        type= request.args.get('type')

        query = {
            'type': type
        }

        document = functional_collection.find_one(query)
        if document:
            return jsonify({'base': document['base']})
        else:
            return jsonify({'error': 'base set not found'}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
# Get functional rule set
@app.route('/get_functional_rule_set', methods=['GET'])
def get_functional_rule_set():
    try:
        
        type= request.args.get('type')

        query = {
            'type': type
        }

        document = functional_collection.find_one(query)
        if document:
            return jsonify({'rule_set': document['rule_set']})
        else:
            return jsonify({'error': 'Rule Set not found'}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# update functional base
@app.route('/update_functional_base', methods=['POST'])
def update_functional_base():
    data = request.json
    type = data.get('type')
    base = data.get('base')

    query = {
        'type': type
    }
    
    update = {
        '$set': {'base': base,'update_base_flag': 1}
    }

    result = functional_collection.update_one(query, update)
    
    if result.matched_count:
        return jsonify({'success': 'Base Set updated successfully'})
    else:
        return jsonify({'error': 'No prompt found for the given criteria'}), 404
    
# Add rule to the functional rule set
@app.route('/add_functional_rule', methods=['POST'])
def add_functional_rule():
    data = request.json
    type = data.get('type')
    new_rule = data.get('newRule')

    query = {
        'type': type
    }
    
    update = {
        '$push': {'rule_set': new_rule,'add_rule_flag': 1}
    }
    
    result = functional_collection.update_one(query, update)
    
    if result.matched_count:
        return jsonify({'success': 'Rule added successfully'})
    else:
        return jsonify({'error': 'No document found for the given criteria'}), 404
    
# Update rule in the functional rule set
@app.route('/update_functional_rule', methods=['POST'])
def update_functional_rule():
    data = request.json
    type = data.get('type')
    index = data.get('index')
    updated_rule = data.get('updatedRule')

    query = {
        'type': type
    }
    
    update = {
        '$set': {f'rule_set.{index}': updated_rule,'update_rule_flag': 1}
    }
    
    result = functional_collection.update_one(query, update)
    
    if result.matched_count:
        return jsonify({'success': 'Rule updated successfully'})
    else:
        return jsonify({'error': 'No document found for the given criteria'}), 404
    
# Delete rule from the functional rule set
@app.route('/delete_functional_rule', methods=['POST'])
def delete_functional_rule():
    try:
        data = request.json
        type = data.get('type')
        index = data.get('index')

        query = {
            'type': type
        }

        document = functional_collection.find_one(query)
        if not document:
            return jsonify({'error': 'No document found for the given criteria'}), 404

        rule_set = document.get('rule_set', [])
        if index < 0 or index >= len(rule_set):
            return jsonify({'error': 'Index out of bounds'}), 400

        # Remove the rule at the specified index
        rule_set.pop(index)

        # Update the document with the modified rule_set
        update = {
            '$set': {'rule_set': rule_set,'update_rule_flag': 1}
        }

        result = functional_collection.update_one(query, update)

        if result.modified_count:
            return jsonify({'success': 'Rule deleted successfully'})
        else:
            return jsonify({'error': 'Failed to update the document'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#update functional rule set order
@app.route('/update_functional_rule_set', methods=['POST'])
def update_functional_rule_set():
    try:
        data = request.json
        type = data.get('type')
        new_rule_set = data.get('rule_set')

        query = {
            'type': type
        }

        update = {
            '$set': {'rule_set': new_rule_set,'update_rule_flag': 1}
        }

        result = functional_collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Rule set updated successfully'})
        else:
            return jsonify({'error': 'No document found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Get answer agent prompt
@app.route('/get_answer_agent_prompt', methods=['GET'])
def get_answer_prompt():
    try:
        grade = request.args.get('grade')
        prompt_style = request.args.get('prompt_style')
        subject = request.args.get('subject')
        topic = request.args.get('topic')

        query = {
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        }

        document = answer_agent_collection.find_one(query)
        if document:
            return jsonify({'prompt': document['prompt']})
        else:
            return jsonify({'error': 'Prompt not found'}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Get answer agent base set
@app.route('/get_answer_agent_base', methods=['GET'])
def get_answer_base():
    try:
        grade = request.args.get('grade')
        prompt_style = request.args.get('prompt_style')
        subject = request.args.get('subject')
        topic = request.args.get('topic')

        query = {
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        }

        document = answer_agent_collection.find_one(query)
        if document:
            return jsonify({'base': document['base']})
        else:
            return jsonify({'error': 'base set not found'}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get answer agent rule set
@app.route('/get_answer_agent_rule_set', methods=['GET'])
def get_answer_rule_set():
    try:
        grade = request.args.get('grade')
        prompt_style = request.args.get('prompt_style')
        subject = request.args.get('subject')
        topic = request.args.get('topic')

        query = {
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        }

        document = answer_agent_collection.find_one(query)
        if document:
            return jsonify({'rule_set': document['rule_set']})
        else:
            return jsonify({'error': 'Rule Set not found'}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# update answer agent base
@app.route('/update_answer_agent_base', methods=['POST'])
def update_answer_base():
    data = request.json
    grade = data.get('grade')
    prompt_style = data.get('prompt_style')
    subject = data.get('subject')
    topic = data.get('topic')
    base = data.get('base')

    query = {
        'grade': grade,
        'prompt_style': prompt_style,
        'subject': subject,
        'topic': topic
    }
    
    update = {
        '$set': {'base': base,'update_base_flag': 1}
    }

    result = answer_agent_collection.update_one(query, update)
    
    if result.matched_count:
        return jsonify({'success': 'Base Set updated successfully'})
    else:
        return jsonify({'error': 'No prompt found for the given criteria'}), 404
    
# Add rule to the answer agent rule set
@app.route('/add_answer_agent_rule', methods=['POST'])
def add_answer_rule():
    data = request.json
    grade = data.get('grade')
    prompt_style = data.get('prompt_style')
    subject = data.get('subject')
    topic = data.get('topic')
    new_rule = data.get('newRule')

    query = {
        'grade': grade,
        'prompt_style': prompt_style,
        'subject': subject,
        'topic': topic
    }

    update = {
        '$push': {'rule_set': new_rule,'add_rule_flag': 1}
    }

    result = answer_agent_collection.update_one(query, update)

    if result.matched_count:
        return jsonify({'success': 'Rule added successfully'})
    else:
        return jsonify({'error': 'No document found for the given criteria'}), 404
    
# Update rule in the answer agent rule set
@app.route('/update_answer_agent_rule', methods=['POST'])
def update_answer_rule():
    data = request.json
    grade = data.get('grade')
    prompt_style = data.get('prompt_style')
    subject = data.get('subject')
    topic = data.get('topic')
    index = data.get('index')
    updated_rule = data.get('updatedRule')

    query = {
        'grade': grade,
        'prompt_style': prompt_style,
        'subject': subject,
        'topic': topic
    }

    update = {
        '$set': {f'rule_set.{index}': updated_rule,'update_rule_flag': 1}
    }

    result = answer_agent_collection.update_one(query, update)

    if result.matched_count:
        return jsonify({'success': 'Rule updated successfully'})
    else:
        return jsonify({'error': 'No document found for the given criteria'}), 404
    
# Delete rule from the answer agent rule set
@app.route('/delete_answer_agent_rule', methods=['POST'])
def delete_answer_rule():
    try:
        data = request.json
        grade = data.get('grade')
        prompt_style = data.get('prompt_style')
        subject = data.get('subject')
        topic = data.get('topic')
        index = data.get('index')

        query = {
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        }

        document = answer_agent_collection.find_one(query)
        if not document:
            return jsonify({'error': 'No document found for the given criteria'}), 404

        rule_set = document.get('rule_set', [])
        if index < 0 or index >= len(rule_set):
            return jsonify({'error': 'Index out of bounds'}), 400

        # Remove the rule at the specified index
        rule_set.pop(index)

        # Update the document with the modified rule_set
        update = {
            '$set': {'rule_set': rule_set,'update_rule_flag': 1}
        }

        result = answer_agent_collection.update_one(query, update)

        if result.modified_count:
            return jsonify({'success': 'Rule deleted successfully'})
        else:
            return jsonify({'error': 'Failed to update the document'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#update answer agent rule set order
@app.route('/update_answer_agent_rule_set', methods=['POST'])
def update_answer_rule_set():
    try:
        data = request.json
        grade = data.get('grade')
        prompt_style = data.get('prompt_style')
        subject = data.get('subject')
        topic = data.get('topic')
        new_rule_set = data.get('rule_set')

        query = {
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        }

        update = {
            '$set': {'rule_set': new_rule_set,'update_rule_flag': 1}
        }

        result = answer_agent_collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Rule set updated successfully'})
        else:
            return jsonify({'error': 'No document found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# add answer agent rule to all documnets of a topic    
@app.route('/add_answer_agent_rule_to_topic', methods=['POST'])
def add_answer_rule_to_topic():
    try:
        data = request.json
        topic = data.get('topic')
        new_rule = data.get('newRule')

        if not topic or not new_rule:
            return jsonify({'error': 'Topic and new rule must be provided'}), 400

        # Find all documents with the given topic
        documents = answer_agent_collection.find({'topic': topic})

        updated_count = 0
        for document in documents:
            rule_set = document.get('rule_set', [])
            if new_rule not in rule_set:
                rule_set.append(new_rule)
                answer_agent_collection.update_one(
                    {'_id': document['_id']},
                    {'$set': {'rule_set': rule_set}, 'update_rule_flag': 1}
                )
                updated_count += 1

        return jsonify({'success': f'Rule added to {updated_count} documents'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# revert base
@app.route('/revert_base', methods=['POST'])
def revert_base():
    try:
        data = request.json
        grade = data.get('grade')
        interaction = data.get('interaction')
        learning_method = data.get('learning_method')
        subject = data.get('subject')
        topic = data.get('topic')

        query = {
            'grade': grade,
            'interaction': interaction,
            'learning_method': learning_method,
            'subject': subject,
            'topic': topic
        }

        original_collection = collection_original
        original_document = original_collection.find_one(query)
        if not original_document:
            return jsonify({'error': 'Original base not found for the given criteria'}), 404

        original_base = original_document['base']

        update = {
            '$set': {
                'base': original_base,
                'update_base_flag': 0
            }
        }

        result = collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Base Set reverted successfully'})
        else:
            return jsonify({'error': 'No prompt found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# revert rule set
@app.route('/revert_rule_set', methods=['POST'])
def revert_rule_set():
    try:
        data = request.json
        grade = data.get('grade')
        interaction = data.get('interaction')
        learning_method = data.get('learning_method')
        subject = data.get('subject')
        topic = data.get('topic')

        query = {
            'grade': grade,
            'interaction': interaction,
            'learning_method': learning_method,
            'subject': subject,
            'topic': topic
        }

        original_collection = collection_original
        original_document = original_collection.find_one(query)
        if not original_document:
            return jsonify({'error': 'Original rule set not found for the given criteria'}), 404

        original_rule_set = original_document['rule_set']

        update = {
            '$set': {
                'rule_set': original_rule_set,
                'update_rule_flag': 0
            }
        }

        result = collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Rule Set reverted successfully'})
        else:
            return jsonify({'error': 'No prompt found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# revert functional base
@app.route('/revert_functional_base', methods=['POST'])
def revert_functional_base():
    try:
        data = request.json
        type = data.get('type')

        query = {
            'type': type
        }

        original_collection = functional_collection_original
        original_document = original_collection.find_one(query)
        if not original_document:
            return jsonify({'error': 'Original base not found for the given criteria'}), 404

        original_base = original_document['base']

        update = {
            '$set': {
                'base': original_base,
                'update_base_flag': 0
            }
        }

        result = functional_collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Base Set reverted successfully'})
        else:
            return jsonify({'error': 'No prompt found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# revert functional rule set
@app.route('/revert_functional_rule_set', methods=['POST'])
def revert_functional_rule_set():
    try:
        data = request.json
        type = data.get('type')

        query = {
            'type': type
        }

        original_collection = functional_collection_original
        original_document = original_collection.find_one(query)
        if not original_document:
            return jsonify({'error': 'Original rule set not found for the given criteria'}), 404

        original_rule_set = original_document['rule_set']

        update = {
            '$set': {
                'rule_set': original_rule_set,
                'update_rule_flag': 0
            }
        }

        result = functional_collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Rule Set reverted successfully'})
        else:
            return jsonify({'error': 'No prompt found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# revert answer agent base
@app.route('/revert_answer_agent_base', methods=['POST'])
def revert_answer_base():
    try:
        data = request.json
        grade = data.get('grade')
        prompt_style = data.get('prompt_style')
        subject = data.get('subject')
        topic = data.get('topic')

        query = {
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        }

        original_collection = answer_agent_collection_original
        original_document = original_collection.find_one(query)
        if not original_document:
            return jsonify({'error': 'Original base not found for the given criteria'}), 404

        original_base = original_document['base']

        update = {
            '$set': {
                'base': original_base,
                'update_base_flag': 0
            }
        }

        result = answer_agent_collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Base Set reverted successfully'})
        else:
            return jsonify({'error': 'No prompt found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# revert answer agent rule set
@app.route('/revert_answer_agent_rule_set', methods=['POST'])
def revert_answer_rule_set():
    try:
        data = request.json
        grade = data.get('grade')
        prompt_style = data.get('prompt_style')
        subject = data.get('subject')
        topic = data.get('topic')

        query = {
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        }

        original_collection = answer_agent_collection_original
        original_document = original_collection.find_one(query)
        if not original_document:
            return jsonify({'error': 'Original rule set not found for the given criteria'}), 404

        original_rule_set = original_document['rule_set']

        update = {
            '$set': {
                'rule_set': original_rule_set,
                'update_rule_flag': 0
            }
        }

        result = answer_agent_collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Rule Set reverted successfully'})
        else:
            return jsonify({'error': 'No prompt found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#update prompt from base and rule set
@app.route('/update_answer_agent_prompts', methods=['POST'])
def update_answer_prompts():
    try:
        data = request.json
        grade = data.get('grade')
        prompt_style = data.get('prompt_style')
        subject = data.get('subject')
        topic = data.get('topic')
        print(grade,prompt_style,subject,topic)
        if not grade or not prompt_style or not subject or not topic:
            return jsonify({'error': 'Missing required parameters'}), 400

        # Fetch base set
        base_document = answer_agent_collection.find_one({
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        })

        if not base_document:
            return jsonify({'error': 'Base set not found'}), 404

        base_set = base_document.get('base', '')

        # Fetch rule set
        rule_document = answer_agent_collection.find_one({
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        })

        if not rule_document:
            return jsonify({'error': 'Rule set not found'}), 404

        rule_set = rule_document.get('rule_set', [])

        # Combine base set and rule set
        combined_prompts = base_set + ' ' + ' '.join(rule_set)

        # Update prompts field
        result = answer_agent_collection.update_one({
            'grade': grade,
            'prompt_style': prompt_style,
            'subject': subject,
            'topic': topic
        }, {
            '$set': {'prompt': combined_prompts}
        })

        if result.modified_count:
            return jsonify({'success': 'Prompts updated successfully'})
        else:
            return jsonify({'error': 'Failed to update prompts'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_prompt', methods=['GET'])
def get_prompt():
    try:
        grade = request.args.get('grade')
        interaction = request.args.get('interaction')
        learning_method = request.args.get('learning_method')
        subject = request.args.get('subject')
        topic = request.args.get('topic')

        query = {
            'grade': grade,
            'interaction': interaction,
            'learning_method': learning_method,
            'subject': subject,
            'topic': topic
        }

        document = collection.find_one(query)
        if document:
            return jsonify({'prompt': document['prompt']})
        else:
            return jsonify({'error': 'Prompt not found'}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
       
#get base 
@app.route('/get_base', methods=['GET'])
def get_base():
    try:
        grade = request.args.get('grade')
        interaction = request.args.get('interaction')
        learning_method = request.args.get('learning_method')
        subject = request.args.get('subject')
        topic = request.args.get('topic')

        query = {
            'grade': grade,
            'interaction': interaction,
            'learning_method': learning_method,
            'subject': subject,
            'topic': topic
        }

        document = collection.find_one(query)
        if document:
            return jsonify({'base': document['base']})
        else:
            return jsonify({'error': 'Base Set not found'}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# get rule set    
@app.route('/get_rule_set', methods=['GET'])
def get_rule_set():
    try:
        grade = request.args.get('grade')
        interaction = request.args.get('interaction')
        learning_method = request.args.get('learning_method')
        subject = request.args.get('subject')
        topic = request.args.get('topic')

        query = {
            'grade': grade,
            'interaction': interaction,
            'learning_method': learning_method,
            'subject': subject,
            'topic': topic
        }

        document = collection.find_one(query)
        if document:
            return jsonify({'rule_set': document['rule_set']})
        else:
            return jsonify({'error': 'Rule Set not found'}), 404
    except errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': f'MongoDB connection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# update base
@app.route('/update_base', methods=['POST'])
def update_base():
    data = request.json
    grade = data.get('grade')
    interaction = data.get('interaction')
    learning_method = data.get('learningMethod')
    subject = data.get('subject')
    topic = data.get('topic')
    base = data.get('base')

    query = {
        'grade': grade,
        'interaction': interaction,
        'learning_method': learning_method,
        'subject': subject,
        'topic': topic
    }
    
    update = {
        '$set': {'base': base}
    }

    result = collection.update_one(query, update)
    
    if result.matched_count:
        return jsonify({'success': 'Base Set updated successfully'})
    else:
        return jsonify({'error': 'No prompt found for the given criteria'}), 404
    
# Add rule to the rule set
@app.route('/add_rule', methods=['POST'])
def add_rule():
    data = request.json
    grade = data.get('grade')
    interaction = data.get('interaction')
    learning_method = data.get('learningMethod')
    subject = data.get('subject')
    topic = data.get('topic')
    new_rule = data.get('newRule')

    query = {
        'grade': grade,
        'interaction': interaction,
        'learning_method': learning_method,
        'subject': subject,
        'topic': topic
    }

    update = {
        '$push': {'rule_set': new_rule,'add_rule_flag': 1}
    }

    result = collection.update_one(query, update)

    if result.matched_count:
        return jsonify({'success': 'Rule added successfully'})
    else:
        return jsonify({'error': 'No document found for the given criteria'}), 404

# Update rule in the rule set
@app.route('/update_rule', methods=['POST'])
def update_rule():
    data = request.json
    grade = data.get('grade')
    interaction = data.get('interaction')
    learning_method = data.get('learningMethod')
    subject = data.get('subject')
    topic = data.get('topic')
    index = data.get('index')
    updated_rule = data.get('updatedRule')

    query = {
        'grade': grade,
        'interaction': interaction,
        'learning_method': learning_method,
        'subject': subject,
        'topic': topic
    }

    update = {
        '$set': {f'rule_set.{index}': updated_rule,'update_rule_flag': 1}
    }

    result = collection.update_one(query, update)

    if result.matched_count:
        return jsonify({'success': 'Rule updated successfully'})
    else:
        return jsonify({'error': 'No document found for the given criteria'}), 404

# Delete rule from the rule set
@app.route('/delete_rule', methods=['POST'])
def delete_rule():
    try:
        data = request.json
        grade = data.get('grade')
        interaction = data.get('interaction')
        learning_method = data.get('learningMethod')
        subject = data.get('subject')
        topic = data.get('topic')
        index = data.get('index')

        query = {
            'grade': grade,
            'interaction': interaction,
            'learning_method': learning_method,
            'subject': subject,
            'topic': topic
        }

        document = collection.find_one(query)
        if not document:
            return jsonify({'error': 'No document found for the given criteria'}), 404

        rule_set = document.get('rule_set', [])
        if index < 0 or index >= len(rule_set):
            return jsonify({'error': 'Index out of bounds'}), 400

        # Remove the rule at the specified index
        rule_set.pop(index)

        # Update the document with the modified rule_set
        update = {
            '$set': {'rule_set': rule_set,'update_rule_flag': 1}
        }

        result = collection.update_one(query, update)

        if result.modified_count:
            return jsonify({'success': 'Rule deleted successfully'})
        else:
            return jsonify({'error': 'Failed to update the document'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#update rule set order
@app.route('/update_rule_set', methods=['POST'])
def update_rule_set():
    try:
        data = request.json
        grade = data.get('grade')
        interaction = data.get('interaction')
        learning_method = data.get('learningMethod')
        subject = data.get('subject')
        topic = data.get('topic')
        new_rule_set = data.get('rule_set')

        query = {
            'grade': grade,
            'interaction': interaction,
            'learning_method': learning_method,
            'subject': subject,
            'topic': topic
        }

        update = {
            '$set': {'rule_set': new_rule_set,'update_rule_flag': 1}
        }

        result = collection.update_one(query, update)

        if result.matched_count:
            return jsonify({'success': 'Rule set updated successfully'})
        else:
            return jsonify({'error': 'No document found for the given criteria'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add rule to all documents with the given subject
@app.route('/add_rule_to_subject', methods=['POST'])
def add_rule_to_subject():
    try:
        data = request.json
        subject = data.get('subject')
        new_rule = data.get('newRule')

        if not subject or not new_rule:
            return jsonify({'error': 'Subject and new rule must be provided'}), 400

        # Find all documents with the given subject
        documents = collection.find({'subject': subject})

        updated_count = 0
        for document in documents:
            rule_set = document.get('rule_set', [])
            if new_rule not in rule_set:
                rule_set.append(new_rule)
                collection.update_one(
                    {'_id': document['_id']},
                    {'$set': {'rule_set': rule_set}, 'add_rule_flag': 1}
                )
                updated_count += 1

        return jsonify({'success': f'Rule added to {updated_count} documents'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add rule to all documents with the given topic 
@app.route('/add_rule_to_topic', methods=['POST'])
def add_rule_to_topic():
    try:
        data = request.json
        topic = data.get('topic')
        new_rule = data.get('newRule')

        if not topic or not new_rule:
            return jsonify({'error': 'Topic and new rule must be provided'}), 400

        # Find all documents with the given topic
        documents = collection.find({'topic': topic})

        updated_count = 0
        for document in documents:
            rule_set = document.get('rule_set', [])
            # Check if the new rule is already in the rule set
            if new_rule not in [rule[1] for rule in rule_set]:
                # Append the new rule to the rule set with the flag set to 1
                rule_set.append((1, new_rule))
                # Update the document with the modified rule set and the updated topic flag
                collection.update_one(
                    {'_id': document['_id']},
                    {'$set': {'rule_set': rule_set, 'add_topic_rule': 1}}
                )
                updated_count += 1

        return jsonify({'success': f'Rule added to {updated_count} documents'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/add_rule_to_all_documents', methods=['POST'])
def add_rule_to_all_documents():
    try:
        data = request.json
        new_rule = data.get('newRule')
        if not new_rule:
            return jsonify({'error': 'New rule must be provided'}), 400
        documents = collection.find({})
        updated_count = 0
        for document in documents:
            rule_set = document.get('rule_set', [])
            # Check if the new rule is already in the rule set
            if new_rule not in [rule[1] for rule in rule_set]:
                # Append the new rule to the rule set with the flag set to 1
                rule_set.append((0, new_rule))
                # Update the document with the modified rule set and the updated topic flag
                collection.update_one(
                    {'_id': document['_id']},
                    {'$set': {'rule_set': rule_set, 'add_rule_flag': 1}}
                )
                updated_count += 1
        return jsonify({'success': f'Rule added to {updated_count} documents'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#make a consolidated prompt field which is the combination of base and rule set run this for all documents
@app.route('/consolidate_prompts', methods=['POST'])
def update_prompts():
    try:
        documents = collection.find({})
        for document in documents:
            base_set = document.get('base', '')
            rule_set = document.get('rule_set', [])
            # rule_set is a list of tuples with the first element as the flag
            #number the rules
            combined_prompts=base_set+"\n"+"Rules:"+"\n"+' '+'\n'.join([f'{i+1}. {rule[1]}' for i, rule in enumerate(rule_set)])
            collection.update_one(
                {'_id': document['_id']},
                {'$set': {'consolidated_prompt': combined_prompts}}
            )
        return jsonify({'success': 'Consolidated Prompts updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/update_rule_set_structure', methods=['POST'])
def update_rule_set_structure():
    try:
        documents = collection.find({})
        updated_count = 0
        for document in documents:
            rule_set = document.get('rule_set', [])
            # If the rule_set contains strings, convert it to the new structure
            if rule_set and isinstance(rule_set[0], str):
                new_rule_set = [(0, rule) for rule in rule_set]
                collection.update_one(
                    {'_id': document['_id']},
                    {'$set': {'rule_set': new_rule_set}}
                )
                updated_count += 1
        return jsonify({'success': f'Updated rule set structure for {updated_count} documents'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# replace prompt with consolidated prompt
@app.route('/replace_prompt', methods=['POST'])
def replace_prompt():
    try:
        documents = collection.find({})
        updated_count = 0
        for document in documents:
            consolidated_prompt = document.get('consolidated_prompt', '')
            collection.update_one(
                {'_id': document['_id']},
                {'$set': {'prompt': consolidated_prompt}}
            )
            updated_count += 1
        return jsonify({'success': f'Replaced prompt with consolidated prompt for {updated_count} documents'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# make a new field rule_post_delimiter which is the same rule_set array except that delimiter is removed and interaction limit is removed
def clean_rules(rules):
    if rules and "4" in rules[0][1]:
        rules.pop(0)
    rules = [rule for rule in rules if "(#*#*#)" not in rule[1]]

    return rules
@app.route('/add_rule_post_delimiter', methods=['POST'])
def add_rule_post_delimiter():
    try:
        documents = collection.find({})
        updated_count = 0
        for document in documents:
            base_set = document.get('base', '')
            rule_set = document.get('rule_set', [])
            rule_set = clean_rules(rule_set)
            combined_prompts_post_delimiter=base_set+"\n"+"Rules:"+"\n"+' '+'\n'.join([f'{i+1}. {rule[1]}' for i, rule in enumerate(rule_set)])
            collection.update_one(
                {'_id': document['_id']},
                {'$set': {'rule_post_delimiter': combined_prompts_post_delimiter}}
            )
            updated_count += 1
        return jsonify({'success': f'Added rule_post_delimiter field for {updated_count} documents'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
#update the rule_set from prompt
@app.route('/update_rule_set_from_prompt', methods=['POST'])
def update_rule_set_from_prompt():
    try:
        documents = collection.find({})
        updated_count = 0
        for document in documents:
            prompt = document.get('prompt', '')
            # search for the string "Rules:" in the prompt
            if "Rules:" not in prompt:
                base = prompt
                rule = []
            else:
                base, rules = prompt.split("Rules:")
                rules_lines = rules.strip().split("\n")
                delimiter_rule = rules_lines[-1].strip()
                rules_lines = rules_lines[:-1] 
                rule = [ruled.split(")", 1)[1].strip() for ruled in rules_lines if ")" in ruled]
                rule.append(delimiter_rule)
            collection.update_one(
                {'_id': document['_id']},
                {'$set': {'rule_set': rule}}
            )
            updated_count += 1
        return jsonify({'success': f'Updated rule set from prompt for {updated_count} documents'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# keep the delimiter in rule at the end
@app.route('/keep_delimiter_in_rule', methods=['POST'])
def exchange_rules():
    documents = collection.find()
    for doc in documents:
        rule_set = doc.get('rule_set', [])
        if len(rule_set) >= 2:
            # Exchange the last and second last rules
            rule_set[-1], rule_set[-2] = rule_set[-2], rule_set[-1]
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"rule_set": rule_set}}
            )
    return jsonify({"message": "Last and second last rules exchanged for all documents successfully"}), 200




    
if __name__ == '__main__':
    app.run(debug=True)
