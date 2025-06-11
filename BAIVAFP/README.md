# Building AI Voice Agents for Production


### Before Install 

```bash

    conda create -n myenv python=3.10

    --------------------------------------------------------- START HERE

    conda activate myenv
    conda deactivate                   (deactivatethe env)

    conda install jupyter
    jupyter notebook

    uvicorn main:app --reload

```

### Install

```bash
    pip install -r requirements.txt
```

### Create a .env file in your project directory with:

```bash

    OPENAI_API_KEY=your_actual_api_key_here
    ELEVEN_API_KEY=your_elevenlabs_api_key_here
 ```
