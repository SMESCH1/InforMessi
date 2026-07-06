"""Tests para el filtrado de noticias basura y dedupe multi-día (Fase 6).

Cubre:
- fetch-news.py: blacklist de keywords + exigencia de señal futbolística fuerte
  antes de descartar por blacklist (para no tirar noticias legítimas que
  mencionan de pasada una palabra de la blacklist).
- fetch-news.py: filter_news_llm (best-effort, fallback silencioso ante error).
- scrape-daily-news.py: dedupe de títulos contra los daily-news de los
  últimos N días (no solo dentro del mismo scrape).
"""

import json
import sys
from importlib import import_module
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

fetch_news = import_module("fetch-news")
scrape_daily_news = import_module("scrape-daily-news")


# --- Helpers para armar noticias de prueba ---

def make_news(title, description="", published_at="2026-06-27T09:00:00Z", url=None, source="Test"):
    return {
        "title": title,
        "description": description,
        "url": url or f"https://example.com/{abs(hash(title))}",
        "source": source,
        "published_at": published_at,
    }


# =====================================================================
# 1. Blacklist de keywords — basura real encontrada en data/daily-news/
# =====================================================================

class TestBlacklistDescartaBasura:
    def test_telecom_digi_rechazada(self):
        """'Digi ha perdido el tren del Mundial' es sobre un operador rumano
        de telecomunicaciones, no fútbol — debe ser rechazada aunque el
        título contenga 'Mundial'."""
        news = [make_news(
            "Digi ha perdido el tren del Mundial: el fútbol sigue siendo su gran cuenta pendiente",
            "A pesar de que las tarifas anti-Digi le están robando clientes, el operador rumano...",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_borja_iglesias_coche_rechazada(self):
        """Nota de autos de lujo de un futbolista, no noticia futbolística."""
        news = [make_news(
            "Con millones en la cartera, Borja Iglesias presume de un coche con historia que compró por internet",
            "Hay futbolistas que se compran Ferraris, Lamborghinis y SUVs de 200.000 euros...",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_opinion_politica_rechazada(self):
        """Columna de opinión política/económica, no nota futbolística."""
        news = [make_news(
            "Enrique Galván Ochoa: Dinero",
            "La fiebre del futbol se ha extendido a todos los rincones del mundo...",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    @pytest.mark.parametrize("title,description", [
        ("El Gobierno confirmó nuevas medidas económicas tras las elecciones", ""),
        ("La quiniela y las apuestas del fin de semana: cuotas y pronósticos", ""),
        ("Las acciones de la bolsa suben tras el anuncio del Congreso", ""),
    ])
    def test_blacklist_generica_sin_contexto_futbolistico(self, title, description):
        news = [make_news(title, description)]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_farandula_milei_scaloni_almuerzo_rechazada(self):
        """Dos nombres propios (Milei no es jugador, pero 'Scaloni' es señal
        fuerte) en una nota de chimento no deben anular la blacklist: los
        nombres propios solos no acreditan que la nota sea futbolística."""
        news = [make_news(
            "Milei y Scaloni compartieron un almuerzo en la Casa Rosada",
            "El chimento del año: la Casa Rosada organizó un evento social "
            "con la Scaloneta en el marco de la farándula porteña.",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_farandula_messi_rulli_escandalo_rechazada(self):
        """'Messi' y 'Rulli' son nombres de jugadores (señales fuertes) pero
        la nota es un escándalo de farándula, no fútbol: dos nombres propios
        sin ningún término futbolístico no-nombre-propio no deben anular la
        blacklist."""
        news = [make_news(
            "El escándalo amoroso entre Messi y Rulli sacude la farándula del Congreso",
            "",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_entrenador_personal_gimnasio_lujo_rechazada(self):
        """Ronda 2: bypass reproducido por el reviewer. 'entrenador' es un
        término de contexto ambiguo (entrenador personal de gimnasio, no
        DT de fútbol) y 'jugador' en la descripción también es ambiguo (de
        poker). Ninguno de los dos debería alcanzar para anular la
        blacklist ('escándalo', 'mansión', 'farándula')."""
        news = [make_news(
            "El escándalo de Messi y su entrenador personal en el gimnasio de lujo",
            "Se supo que es jugador de poker... mansión escándalo de la farándula",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_messi_di_maria_partido_truco_rechazada(self):
        """Ronda 2: bypass reproducido por el reviewer. 'partido' en 'partido
        de truco' es un término ambiguo (no futbolístico en este contexto).
        Dos nombres propios (Messi, Di María) + un término ambiguo no deben
        anular la blacklist ('farándula', 'casino', 'polémica amorosa')."""
        news = [make_news(
            "Messi y Di María fueron vistos en un partido de truco",
            "Chimento: la farándula... casino y polémica amorosa",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_messi_estadio_eventos_escandalo_rechazada(self):
        """Ronda 3: 'estadio' fue removido de FOOTBALL_UNAMBIGUOUS_TERMS
        porque es ambiguo (estadio de eventos, etc.). Solo con Messi (nombre
        propio) + 'estadio' (término de contexto ambiguo) + blacklist
        ('escándalo', 'farándula'), no debe pasar: no es suficiente señal
        futbolística inequívoca."""
        news = [make_news(
            "Messi compró un estadio de eventos y quedó envuelto en un escándalo de la farándula",
            "",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_messi_mundial_empanada_farándula_rechazada(self):
        """Ronda 3: 'mundial' fue removido de FOOTBALL_UNAMBIGUOUS_TERMS
        porque es ambiguo fuera de fútbol (Mundial de la Empanada, etc.).
        Solo con Messi (nombre propio) + 'mundial' (término ambiguo) +
        rumores de farándula, no debe pasar: 'mundial' solo no es suficiente
        sin otras señales inequívocas."""
        news = [make_news(
            "Messi participó del Mundial de la Empanada, en medio de rumores de la farándula",
            "",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_messi_amistoso_poker_escandalo_rechazada(self):
        """Ronda 3: 'amistoso' fue removido de FOOTBALL_UNAMBIGUOUS_TERMS
        porque es ambiguo (amistoso de otra actividad). Solo con Messi
        (nombre propio) + 'amistoso' (término de contexto ambiguo) +
        'escándalo' + 'apuestas', no debe pasar: 'amistoso' solo no es
        suficiente señal futbolística inequívoca."""
        news = [make_news(
            "Messi jugó un amistoso de poker con amigos, escándalo de la farándula por las apuestas",
            "",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []


# =====================================================================
# 2. Blacklist NO debe descartar noticias legítimas de fútbol que
#    mencionan de pasada una palabra de la blacklist
# =====================================================================

class TestBlacklistNoRechazaFalsosPositivos:
    def test_gobierno_fifa_con_señal_fuerte_no_se_descarta(self):
        """'el gobierno de la FIFA...' es fútbol — 'fifa' es señal fuerte,
        no debe caer aunque 'gobierno' esté en la blacklist."""
        news = [make_news(
            "El gobierno de la FIFA definió el nuevo formato de eliminatorias",
            "La federación anunció cambios en el reglamento del Mundial 2026.",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert len(result) == 1

    def test_seleccion_argentina_con_mencion_a_congreso_no_se_descarta(self):
        news = [make_news(
            "La Selección Argentina fue recibida en el Congreso tras ganar el Mundial",
            "Scaloni y el plantel campeón visitaron el Congreso de la Nación.",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert len(result) == 1

    def test_messi_menciona_acciones_de_marketing_no_se_descarta(self):
        news = [make_news(
            "Messi lanzó nuevas acciones de marketing junto a la AFA para el Mundial",
            "El capitán de la Selección participó del lanzamiento de la campaña oficial.",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert len(result) == 1

    def test_congreso_fifa_mundial_dos_senales_no_nombre_propio_no_se_descarta(self):
        """'fifa' y 'mundial' son dos señales fuertes no-nombre-propio:
        deben anular la blacklist ('congreso') igual que antes del fix."""
        news = [make_news(
            "El congreso de la FIFA aprobó cambios para el Mundial",
            "",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert len(result) == 1


# =====================================================================
# 3. Keyword fuerte: "argentina" solo no alcanza
# =====================================================================

class TestSeñalFutbolisticaFuerte:
    def test_solo_argentina_sin_contexto_futbol_rechazada(self):
        news = [make_news(
            "Argentina anunció un acuerdo comercial con Brasil",
            "El ministerio de relaciones exteriores confirmó el nuevo tratado.",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert result == []

    def test_seleccion_argentina_confirmo_lista_aceptada(self):
        news = [make_news(
            "La Selección argentina confirmó la lista de convocados",
            "Scaloni dio a conocer los 26 jugadores citados para el Mundial 2026.",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert len(result) == 1

    def test_messi_hablo_tras_la_victoria_aceptada(self):
        news = [make_news(
            "Messi habló tras la victoria",
            "El capitán se refirió al triunfo de la Selección en la última fecha.",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert len(result) == 1

    def test_argentina_mas_termino_futbol_aceptada(self):
        news = [make_news(
            "Argentina ganó el partido con un gol agónico en el estadio",
            "",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert len(result) == 1

    def test_jugador_actual_de_players_json_aceptada(self):
        """Un nombre de jugador convocado (players.json) cuenta como señal
        fuerte aunque el título no diga 'selección' ni 'argentina'."""
        news = [make_news(
            "Emiliano Martínez fue elegido mejor arquero de la fecha",
            "El Dibu atajó un penal decisivo en el cierre del partido.",
        )]
        result = fetch_news._validate_news_basic(news, reference_date="2026-06-28")
        assert len(result) == 1


# =====================================================================
# 4. filter_news_llm
# =====================================================================

class TestFilterNewsLlm:
    def test_json_valido_filtra_por_indices(self):
        news = [
            make_news("Messi habló tras la victoria de Argentina"),
            make_news("El clima en Buenos Aires para mañana"),
            make_news("Scaloni confirmó la lista de convocados"),
        ]
        mock_response = json.dumps({"relevantes": [0, 2]})
        with patch.object(fetch_news, "call_groq", return_value=mock_response) as mock_call:
            result = fetch_news.filter_news_llm(news)
        assert mock_call.called
        assert len(result) == 2
        assert result[0]["title"] == news[0]["title"]
        assert result[1]["title"] == news[2]["title"]

    def test_excepcion_retorna_lista_original(self):
        news = [make_news("Messi habló tras la victoria")]
        with patch.object(fetch_news, "call_groq", side_effect=Exception("boom")):
            result = fetch_news.filter_news_llm(news)
        assert result == news

    def test_error_real_llm_loguea_warning(self, caplog):
        """Errores reales (red, parsing, etc.) deben loguearse como warning,
        no como info — distinto del caso esperado sin GROQ_API_KEY."""
        news = [make_news("Messi habló tras la victoria")]
        with patch.object(fetch_news, "call_groq", side_effect=Exception("timeout de red")):
            with caplog.at_level("WARNING", logger=fetch_news.logger.name):
                fetch_news.filter_news_llm(news)
        assert any(
            record.levelname == "WARNING" and "timeout de red" in record.message
            for record in caplog.records
        )

    def test_sin_groq_api_key_loguea_info_no_warning(self, monkeypatch, caplog):
        """Falta de GROQ_API_KEY es un caso esperado (best-effort sin LLM
        configurado), no un error real: debe loguearse como info/debug, sin
        emitir ningún warning."""
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        news = [make_news("Messi habló tras la victoria")]
        with caplog.at_level("INFO", logger=fetch_news.logger.name):
            fetch_news.filter_news_llm(news)
        assert not any(record.levelname == "WARNING" for record in caplog.records)
        assert any(
            record.levelname == "INFO" and "GROQ_API_KEY" in record.message
            for record in caplog.records
        )

    def test_json_invalido_retorna_lista_original(self):
        news = [make_news("Messi habló tras la victoria")]
        with patch.object(fetch_news, "call_groq", return_value="no es json"):
            result = fetch_news.filter_news_llm(news)
        assert result == news

    def test_sin_groq_api_key_retorna_lista_original(self, monkeypatch):
        """call_groq real lanza LLMClientError si no hay GROQ_API_KEY;
        filter_news_llm debe degradar en silencio."""
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        news = [make_news("Messi habló tras la victoria")]
        result = fetch_news.filter_news_llm(news)
        assert result == news

    def test_lista_vacia_no_llama_al_llm(self):
        with patch.object(fetch_news, "call_groq") as mock_call:
            result = fetch_news.filter_news_llm([])
        assert result == []
        assert not mock_call.called

    def test_indices_fuera_de_rango_se_ignoran(self):
        news = [make_news("Messi habló tras la victoria")]
        mock_response = json.dumps({"relevantes": [0, 5, -1]})
        with patch.object(fetch_news, "call_groq", return_value=mock_response):
            result = fetch_news.filter_news_llm(news)
        assert len(result) == 1


# =====================================================================
# 5. Dedupe multi-día en scrape-daily-news.py
# =====================================================================

class TestDedupeMultiDia:
    def _write_daily_news(self, tmp_dir: Path, date: str, titles):
        payload = {
            "scrape_date": date,
            "scraped_at": f"{date}T09:00:00",
            "total_news": len(titles),
            "news": [make_news(t) for t in titles],
        }
        (tmp_dir / f"{date}.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    def test_titulo_repetido_en_dia_anterior_se_descarta(self, tmp_path):
        self._write_daily_news(
            tmp_path, "2026-06-26",
            ["Quién es Lucas Trejo, el árbitro del clásico de mañana"],
        )
        today_news = [
            make_news("¡Quien es Lucas Trejo, el arbitro del clasico de mañana!"),
            make_news("Messi habló tras la victoria de Argentina"),
        ]

        recent_titles = scrape_daily_news.load_recent_titles(
            "2026-06-27", days=3, daily_news_dir=tmp_path
        )
        result = scrape_daily_news.filter_seen_titles(today_news, recent_titles)

        assert len(result) == 1
        assert result[0]["title"] == "Messi habló tras la victoria de Argentina"

    def test_titulo_exacto_repetido_distinta_fuente(self, tmp_path):
        """Caso real: 'Hallan sin vida a la esposa y los hijos del futbolista
        Lucas Trejo...' apareció idéntico en 2026-06-30 y 2026-07-01."""
        titulo = (
            "Hallan sin vida a la esposa y los hijos del futbolista Lucas "
            "Trejo tras los terremotos en Venezuela y 74 horas de búsqueda"
        )
        self._write_daily_news(tmp_path, "2026-06-30", [titulo])
        today_news = [make_news(titulo, source="Otra fuente")]

        recent_titles = scrape_daily_news.load_recent_titles(
            "2026-07-01", days=3, daily_news_dir=tmp_path
        )
        result = scrape_daily_news.filter_seen_titles(today_news, recent_titles)
        assert result == []

    def test_no_descarta_fuera_de_ventana_de_dias(self, tmp_path):
        self._write_daily_news(tmp_path, "2026-06-20", ["Noticia vieja repetida"])
        today_news = [make_news("Noticia vieja repetida")]

        # Ventana de 3 días desde 2026-06-27 no llega a 2026-06-20
        recent_titles = scrape_daily_news.load_recent_titles(
            "2026-06-27", days=3, daily_news_dir=tmp_path
        )
        result = scrape_daily_news.filter_seen_titles(today_news, recent_titles)
        assert len(result) == 1

    def test_no_hay_archivos_previos_no_falla(self, tmp_path):
        today_news = [make_news("Cualquier noticia")]
        recent_titles = scrape_daily_news.load_recent_titles(
            "2026-06-27", days=3, daily_news_dir=tmp_path
        )
        result = scrape_daily_news.filter_seen_titles(today_news, recent_titles)
        assert len(result) == 1

    def test_archivo_json_corrupto_se_ignora(self, tmp_path):
        (tmp_path / "2026-06-26.json").write_text("{ esto no es json", encoding="utf-8")
        today_news = [make_news("Messi habló tras la victoria")]
        recent_titles = scrape_daily_news.load_recent_titles(
            "2026-06-27", days=3, daily_news_dir=tmp_path
        )
        result = scrape_daily_news.filter_seen_titles(today_news, recent_titles)
        assert len(result) == 1


# =====================================================================
# 6. NEWS_LLM_FILTER no debe propagarse al subprocess de fetch-news.py
#    (evitar doble filtrado LLM: una vez adentro del subprocess y otra
#    vez afuera, en main()).
# =====================================================================

class TestNoDobleFiltradoLlm:
    def test_subprocess_env_no_contiene_news_llm_filter(self, monkeypatch):
        """Si NEWS_LLM_FILTER=1 está seteado en el proceso principal, el
        subprocess de fetch-news.py NO debe recibirlo en su env: el filtro
        LLM debe correr una única vez, afuera (en main()), no adentro del
        subprocess también."""
        monkeypatch.setenv("NEWS_LLM_FILTER", "1")

        captured_env = {}

        def fake_run(cmd, **kwargs):
            captured_env.update(kwargs.get("env") or {})
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "[]"
            mock_result.stderr = ""
            return mock_result

        with patch.object(scrape_daily_news.subprocess, "run", side_effect=fake_run) as mock_run:
            scrape_daily_news.scrape_news("2026-06-28")

        assert mock_run.called
        assert "NEWS_LLM_FILTER" not in captured_env

    def test_filtro_exterior_sigue_activo_con_news_llm_filter(self, tmp_path, monkeypatch):
        """El filtro LLM exterior (en main(), después del dedupe multi-día)
        debe seguir activándose con NEWS_LLM_FILTER=1, aunque ya no se
        propague al subprocess. Corremos main() de punta a punta (con
        scrape_news/scrape_reddit mockeados para no tocar red ni
        subprocess) y verificamos que filter_news_llm se invoca."""
        monkeypatch.setenv("NEWS_LLM_FILTER", "1")
        monkeypatch.setattr(scrape_daily_news, "DAILY_NEWS_DIR", tmp_path)

        news = [make_news("Messi habló tras la victoria de Argentina")]

        with patch.object(scrape_daily_news, "scrape_news", return_value=news), \
             patch.object(scrape_daily_news, "scrape_reddit", return_value=[]), \
             patch.object(
                 scrape_daily_news, "filter_news_llm", return_value=news
             ) as mock_filter_llm, \
             patch.object(sys, "argv", ["scrape-daily-news.py", "--date", "2026-06-28"]):
            scrape_daily_news.main()

        mock_filter_llm.assert_called_once()
        output_file = tmp_path / "2026-06-28.json"
        assert output_file.exists()
