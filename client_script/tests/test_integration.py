import pytest
import asyncio
from unittest import mock
from main import receive_tm, send_tc, get_metrics
from typing import AsyncGenerator

@pytest.mark.asyncio
async def test_client_workflow() -> None:
    """
    Test qui simule un workflow complet:
    1. Envoi d'une commande
    2. Réception des données de télémétrie
    3. Requête des métriques
    """
    # Mocks pour toutes les dépendances externes
    with mock.patch("client_script.main.aio_pika.connect_robust") as mock_connect, \
         mock.patch("aiohttp.ClientSession") as mock_session_class, \
         mock.patch("builtins.print") as mock_print:
        
        # Setup pour aio_pika (pour send_tc et receive_tm)
        mock_channel = mock.AsyncMock()
        mock_connection = mock.AsyncMock()
        mock_connection.channel.return_value = mock_channel
        mock_connect.return_value = mock_connection
        
        mock_queue = mock.AsyncMock()
        mock_channel.declare_queue.return_value = mock_queue
        mock_queue_iter = mock.AsyncMock()
        mock_queue.iterator.return_value.__aenter__.return_value = mock_queue_iter
        
        # Simuler un message pour receive_tm
        mock_message = mock.AsyncMock()
        mock_message.body = b"TELEMETRY-DATA"
        mock_queue_iter.__aiter__.return_value = [mock_message]
        
        # Setup pour aiohttp (pour get_metrics)
        mock_session = mock.AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_response = mock.AsyncMock()
        mock_response.json.return_value = {"test": "metric-data"}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        # Pour limiter l'exécution des fonctions avec des boucles infinies
        sleep_future = asyncio.Future()
        sleep_future.set_result(None)
        
        # Exécuter send_tc
        await send_tc(b"COMMAND-DATA")
        
        # Vérifier que le message a été publié
        mock_channel.default_exchange.publish.assert_called_once()
        
        # Limiter l'exécution de receive_tm
        with mock.patch("asyncio.sleep", return_value=sleep_future):
            receive_task = asyncio.create_task(receive_tm())
            await asyncio.sleep(0.1)
            receive_task.cancel()
        
        # Vérifier que receive_tm a correctement traité le message
        mock_queue.bind.assert_called_once_with("tm")
        mock_message.ack.assert_called_once()
        
        # Limiter l'exécution de get_metrics
        with mock.patch("asyncio.sleep", return_value=sleep_future):
            metrics_task = asyncio.create_task(get_metrics())
            await asyncio.sleep(0.1)
            metrics_task.cancel()
        
        # Vérifier que get_metrics a fait les requêtes HTTP
        assert mock_session.get.call_count > 0 