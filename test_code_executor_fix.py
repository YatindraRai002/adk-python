"""Test to verify the code executor infinite loop fix."""
import asyncio
from google.adk import Agent
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.runners import InMemoryRunner
from google.genai import types


async def test_code_executor():
    """Test that code executor doesn't cause infinite loop."""
    root_agent = Agent(
        model='gemini-pro',
        name='hello_world_agent',
        description='hello world agent.',
        instruction="""
        you are an agent that knows how to produce python code.
        """,
        code_executor=UnsafeLocalCodeExecutor(),
    )
    
    app_name = 'test_app'
    user_id = 'test_user'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )
    
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    
    content = types.Content(
        role='user', 
        parts=[types.Part.from_text(text='write python code that computes 2+2.')]
    )
    
    print('Sending request to agent...')
    event_count = 0
    max_events = 20  # Prevent true infinite loop in test
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        event_count += 1
        print(f'Event {event_count}: {event.author} - {type(event.content).__name__ if event.content else "no content"}')
        
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f'  Text: {part.text[:100]}...' if len(part.text) > 100 else f'  Text: {part.text}')
                if part.executable_code:
                    print(f'  Code: {part.executable_code.code[:100]}...')
                if part.code_execution_result:
                    print(f'  Result: {part.code_execution_result.output[:100] if part.code_execution_result.output else "empty"}')
        
        if event_count >= max_events:
            print(f'ERROR: Reached {max_events} events - likely infinite loop!')
            return False
    
    print(f'\nTest completed successfully with {event_count} events')
    return event_count < max_events


if __name__ == '__main__':
    import sys
    sys.path.insert(0, 'c:\\Users\\Asus\\Downloads\\adk-python\\src')
    
    success = asyncio.run(test_code_executor())
    if success:
        print('\n✓ Test PASSED - No infinite loop detected')
    else:
        print('\n✗ Test FAILED - Infinite loop detected')
        sys.exit(1)
