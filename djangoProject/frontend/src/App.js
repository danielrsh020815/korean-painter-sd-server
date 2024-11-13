import React, {useEffect, useState} from 'react';

function App() {
    const [username, setUsername] = useState('');
    const [access, setAccess] = useState('');
    const [refresh, setRefresh] = useState('');
    const [password, setPassword] = useState('');
    const [prompt, setPrompt] = useState('');
    const [promptId, setPromptId] = useState('');
    const [progress, setProgress] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [loginCompleted, setLoginCompleted] = useState(false);
    const [isInferencing, setIsInferencing] = useState(false);
    const [useLLM, setUseLLM] = useState(false);

    const SERVER_URL = process.env.REACT_APP_SERVER_URL;
    let progressInterval = null;  // 진행 상태 확인을 위한 interval 변수

    const handleLogin = async () => {
        try {
            const response = await fetch(`${SERVER_URL}/api/login/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'username': username, 'password': password })
            });
            if (response.ok) {
                response.json().then(data => {
                    setAccess(data.access);
                    setRefresh(data.refresh);
                })
                setLoginCompleted(true);
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    };

    const handlePromptRequest = async () => {
        try {
            const response = await fetch(`${SERVER_URL}/api/prompt/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'access': access, 'prompt': prompt, 'use_llm': useLLM })
            });
            if (response.ok) {
                response.json().then(data => {
                    setPromptId(data.prompt_id);
                })
            }
        } catch (error) {
            console.error('Prompt error:', error);
        }
    };

    useEffect(() => {
        // promptId가 업데이트된 이후에 polling 시작
        if (promptId) {
            startProgressPolling();
        }
    }, [promptId]);  // promptId가 변경될 때만 실행

    const startProgressPolling = () => {
        if (progressInterval) clearInterval(progressInterval);  // 이전 interval이 있다면 정리
        setIsInferencing(true);
        setProgress('0%');
        progressInterval = setInterval(async () => {
            await handleProgressRequest();
        }, 1000);  // 1초 간격으로 진행 상태 요청
    };

    const stopProgressPolling = () => {
        if (progressInterval) {
            clearInterval(progressInterval);  // interval 정리
            progressInterval = null;
            setIsInferencing(false);
        }
    };

    const handleProgressRequest = async () => {
        try {
            const response = await fetch(`${SERVER_URL}/api/progress/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'prompt_id': promptId })
            });
            const data = await response.json();
            if (data.progress === 100) {
                setProgress(`${data.progress}%`);
                await handleImageRequest();
                stopProgressPolling();
            } else {
                setProgress(`${data.progress}%`);
            }
        } catch (error) {
            console.error('Progress error:', error);
        }
    };

    const handleImageRequest = async () => {
        try {
            const response = await fetch(`${SERVER_URL}/api/image/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'prompt_id': promptId })
            });
            const data = await response.json();
            setImageUrl(data.image_url);
        } catch (error) {
            console.error('Image request error:', error);
        }
    };

    return (
        <div>
            <h1>Korean Painter Style Diffusion</h1>

            <div>
                <input
                    type="text"
                    placeholder="ID"
                    value={username}
                    disabled={loginCompleted}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    disabled={loginCompleted}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button onClick={handleLogin} disabled={loginCompleted}>
                    {loginCompleted ? 'Login Completed' : 'Login'}
                </button>
            </div>

            <div>
                <label>
                    <input
                        type="checkbox"
                        checked={useLLM}
                        onChange={_ => setUseLLM(!useLLM)}
                    />
                    Use LLM for better prompt
                </label>
            </div>

            <div>
                <input
                    type="textarea"
                    placeholder="Prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                />
                <button onClick={handlePromptRequest} disabled={isInferencing}>Submit Prompt</button>
            </div>

            <div>
                <p>Prompt ID: {promptId}</p>
                <p>Progress: {progress}</p>
                {imageUrl && <img src={imageUrl} alt="Generated" />}
            </div>
        </div>
    );
}

export default App;
