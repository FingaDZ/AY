module.exports = {
    apps: [
        {
            name: "ay-hr-backend",
            cwd: "/opt/ay-hr/backend",
            script: "/opt/ay-hr/backend/venv/bin/python",
            args: "-m uvicorn main:app --host 0.0.0.0 --port 8000",
            interpreter: "none", // Important pour utiliser le python du venv directement
            env: {
                NODE_ENV: "production",
            },
        },
        {
            name: "ay-hr-frontend",
            cwd: "/opt/ay-hr/frontend",
            script: "npm",
            args: "run preview -- --host 0.0.0.0 --port 3000",
            env: {
                NODE_ENV: "production",
            },
        },
    ],
};
