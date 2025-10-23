import { createSignal } from 'solid-js';

function HelloFetcher() {
    const [message, setMessage] = createSignal('Click to fetch hello from backend');

    const fetchHello = async () => {
        try {
            const response = await fetch('api/hello');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const helloMessage = data.message;
            setMessage(helloMessage);
            console.log('Received message:', helloMessage);
        } catch (error) {
            const errorMessage = `Failed to fetch: ${error.message}`;
            setMessage(errorMessage);
            console.error(errorMessage);
        }
    };

    return (
        <div style={{ textAlign: 'center' }}>
            <button
                onClick={fetchHello}
                style={{ fontSize: '1.125rem', padding: '0.6rem 1rem', cursor: 'pointer', marginBottom: '1rem' }}
            >
                Fetch Hello
            </button>
            <p>{message()}</p>
        </div>
    );
}

export default HelloFetcher;
