{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "cf61148a",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Collecting ansys-mechanical-core\n",
      "  Using cached ansys_mechanical_core-0.12.0-py3-none-any.whl.metadata (11 kB)\n",
      "Collecting ansys-api-mechanical==0.1.3 (from ansys-mechanical-core)\n",
      "  Using cached ansys_api_mechanical-0.1.3-py3-none-any.whl.metadata (2.1 kB)\n",
      "Collecting ansys-mechanical-stubs==0.1.9 (from ansys-mechanical-core)\n",
      "  Using cached ansys_mechanical_stubs-0.1.9-py3-none-any.whl.metadata (11 kB)\n",
      "Collecting ansys-pythonnet>=3.1.0rc6 (from ansys-mechanical-core)\n",
      "  Using cached ansys_pythonnet-3.1.0rc6-py3-none-any.whl.metadata (2.0 kB)\n",
      "Collecting ansys-tools-common>=0.4.0 (from ansys-mechanical-core)\n",
      "  Using cached ansys_tools_common-0.4.1-py3-none-any.whl.metadata (5.4 kB)\n",
      "Requirement already satisfied: appdirs>=1.4.0 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from ansys-mechanical-core) (1.4.4)\n",
      "Requirement already satisfied: click>=8.1.3 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from ansys-mechanical-core) (8.1.7)\n",
      "Collecting clr-loader>=0.2.6 (from ansys-mechanical-core)\n",
      "  Using cached clr_loader-0.2.10-py3-none-any.whl.metadata (1.5 kB)\n",
      "Collecting grpcio>=1.30.0 (from ansys-mechanical-core)\n",
      "  Using cached grpcio-1.76.0-cp312-cp312-win_amd64.whl.metadata (3.8 kB)\n",
      "Requirement already satisfied: protobuf<6,>=3.12.2 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from ansys-mechanical-core) (4.25.3)\n",
      "Collecting psutil>=6 (from ansys-mechanical-core)\n",
      "  Using cached psutil-7.2.1-cp37-abi3-win_amd64.whl.metadata (23 kB)\n",
      "Requirement already satisfied: tqdm>=4.45.0 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from ansys-mechanical-core) (4.66.5)\n",
      "Requirement already satisfied: requests<3,>=2 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from ansys-mechanical-core) (2.32.3)\n",
      "Requirement already satisfied: platformdirs>=3.6 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from ansys-tools-common>=0.4.0->ansys-mechanical-core) (3.10.0)\n",
      "Collecting requests<3,>=2 (from ansys-mechanical-core)\n",
      "  Using cached requests-2.32.5-py3-none-any.whl.metadata (4.9 kB)\n",
      "Collecting scooby>=0.5.12 (from ansys-tools-common>=0.4.0->ansys-mechanical-core)\n",
      "  Using cached scooby-0.11.0-py3-none-any.whl.metadata (15 kB)\n",
      "Requirement already satisfied: typing-extensions>=4.5 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from ansys-tools-common>=0.4.0->ansys-mechanical-core) (4.11.0)\n",
      "Requirement already satisfied: colorama in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from click>=8.1.3->ansys-mechanical-core) (0.4.6)\n",
      "Requirement already satisfied: cffi>=1.17 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from clr-loader>=0.2.6->ansys-mechanical-core) (1.17.1)\n",
      "Collecting typing-extensions>=4.5 (from ansys-tools-common>=0.4.0->ansys-mechanical-core)\n",
      "  Using cached typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)\n",
      "Requirement already satisfied: charset_normalizer<4,>=2 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from requests<3,>=2->ansys-mechanical-core) (3.3.2)\n",
      "Requirement already satisfied: idna<4,>=2.5 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from requests<3,>=2->ansys-mechanical-core) (3.7)\n",
      "Requirement already satisfied: urllib3<3,>=1.21.1 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from requests<3,>=2->ansys-mechanical-core) (2.2.3)\n",
      "Requirement already satisfied: certifi>=2017.4.17 in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from requests<3,>=2->ansys-mechanical-core) (2025.4.26)\n",
      "Requirement already satisfied: pycparser in c:\\users\\dipes\\anaconda3\\lib\\site-packages (from cffi>=1.17->clr-loader>=0.2.6->ansys-mechanical-core) (2.21)\n",
      "Using cached ansys_mechanical_core-0.12.0-py3-none-any.whl (154 kB)\n",
      "Using cached ansys_api_mechanical-0.1.3-py3-none-any.whl (9.4 kB)\n",
      "Using cached ansys_mechanical_stubs-0.1.9-py3-none-any.whl (1.6 MB)\n",
      "Using cached ansys_pythonnet-3.1.0rc6-py3-none-any.whl (297 kB)\n",
      "Using cached ansys_tools_common-0.4.1-py3-none-any.whl (70 kB)\n",
      "Using cached clr_loader-0.2.10-py3-none-any.whl (56 kB)\n",
      "Downloading grpcio-1.76.0-cp312-cp312-win_amd64.whl (4.7 MB)\n",
      "   ---------------------------------------- 0.0/4.7 MB ? eta -:--:--\n",
      "   ----------------- ---------------------- 2.1/4.7 MB 14.7 MB/s eta 0:00:01\n",
      "   ---------------------------------------- 4.7/4.7 MB 15.8 MB/s eta 0:00:00\n",
      "Using cached psutil-7.2.1-cp37-abi3-win_amd64.whl (136 kB)\n",
      "Using cached requests-2.32.5-py3-none-any.whl (64 kB)\n",
      "Using cached scooby-0.11.0-py3-none-any.whl (19 kB)\n",
      "Using cached typing_extensions-4.15.0-py3-none-any.whl (44 kB)\n",
      "Installing collected packages: typing-extensions, scooby, requests, psutil, ansys-mechanical-stubs, grpcio, clr-loader, ansys-tools-common, ansys-pythonnet, ansys-api-mechanical, ansys-mechanical-core\n",
      "  Attempting uninstall: typing-extensions\n",
      "    Found existing installation: typing_extensions 4.11.0\n",
      "    Uninstalling typing_extensions-4.11.0:\n",
      "      Successfully uninstalled typing_extensions-4.11.0\n",
      "  Attempting uninstall: requests\n",
      "    Found existing installation: requests 2.32.3\n",
      "    Uninstalling requests-2.32.3:\n",
      "      Successfully uninstalled requests-2.32.3\n",
      "  Attempting uninstall: psutil\n",
      "    Found existing installation: psutil 5.9.0\n",
      "    Uninstalling psutil-5.9.0:\n",
      "      Successfully uninstalled psutil-5.9.0\n",
      "Successfully installed ansys-api-mechanical-0.1.3 ansys-mechanical-core-0.12.0 ansys-mechanical-stubs-0.1.9 ansys-pythonnet-3.1.0rc6 ansys-tools-common-0.4.1 clr-loader-0.2.10 grpcio-1.76.0 psutil-7.2.1 requests-2.32.5 scooby-0.11.0 typing-extensions-4.15.0\n",
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    }
   ],
   "source": [
    "pip install ansys-mechanical-core"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "2f7c65a6",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Importing libraries...\n",
      "✓ PyMechanical imported\n",
      "✓ All imports successful\n",
      "\n"
     ]
    }
   ],
   "source": [
    "print(\"Importing libraries...\")\n",
    "\n",
    "try:\n",
    "    import ansys.mechanical.core as pymechanical\n",
    "    print(\"✓ PyMechanical imported\")\n",
    "except ImportError:\n",
    "    print(\"❌ ERROR: PyMechanical not installed\")\n",
    "    print(\"Install it with: pip install ansys-mechanical-core\")\n",
    "    raise\n",
    "\n",
    "import pandas as pd\n",
    "import os\n",
    "from pathlib import Path\n",
    "\n",
    "print(\"✓ All imports successful\\n\")\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "base",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
