"""
Generador de Reportes HTML para Behave + Playwright.

Este módulo recopila resultados de ejecución de pruebas y genera un reporte
HTML moderno con gráficos SVG, screenshots embebidos y secciones colapsables.

Uso:
    Se integra automáticamente desde features/environment.py
"""

import os
import json
import shutil
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# ══════════════════════════════════════════════════════════════
# CARGA DE CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / '.env')


def _get_env_bool(key, default=False):
    """Obtiene variable de entorno como booleano."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'si')


def _load_report_config():
    """Carga la configuración del reporte desde report_config.json."""
    config_path = PROJECT_ROOT / 'report_config.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


# Variables de entorno
REPORT_ENABLED = _get_env_bool('REPORT_ENABLED', True)
REPORT_OUTPUT_DIR = os.getenv('REPORT_OUTPUT_DIR', 'reports')
REPORT_FILENAME = os.getenv('REPORT_FILENAME', 'reporte_pruebas.html')
SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR', 'reports/screenshots')
REPORT_CLEAN_BEFORE_RUN = _get_env_bool('REPORT_CLEAN_BEFORE_RUN', True)
SCREENSHOT_ON_EACH_STEP = _get_env_bool('SCREENSHOT_ON_EACH_STEP', True)
SCREENSHOT_ONLY_ON_FAILURE = _get_env_bool('SCREENSHOT_ONLY_ON_FAILURE', False)
REPORT_OPEN_AFTER_RUN = _get_env_bool('REPORT_OPEN_AFTER_RUN', False)

# Rutas absolutas
REPORT_OUTPUT_PATH = PROJECT_ROOT / REPORT_OUTPUT_DIR
SCREENSHOTS_PATH = PROJECT_ROOT / SCREENSHOTS_DIR
REPORT_FILE_PATH = REPORT_OUTPUT_PATH / REPORT_FILENAME


# ══════════════════════════════════════════════════════════════
# CLASE PRINCIPAL - RECOLECTOR DE DATOS
# ══════════════════════════════════════════════════════════════

class ReportCollector:
    """Recopila datos de ejecución de Behave para generar el reporte."""

    def __init__(self):
        self.config = _load_report_config()
        self.features = []
        self.start_time = None
        self.end_time = None
        self._current_feature = None
        self._current_scenario = None
        self._step_counter = 0

    def initialize(self):
        """Inicializa el colector y limpia reportes anteriores si corresponde."""
        if not REPORT_ENABLED:
            return

        if REPORT_CLEAN_BEFORE_RUN:
            self._clean_previous_reports()

        REPORT_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        SCREENSHOTS_PATH.mkdir(parents=True, exist_ok=True)

        self.start_time = datetime.now()
        self._step_counter = 0

    def _clean_previous_reports(self):
        """Limpia reportes y screenshots anteriores."""
        if SCREENSHOTS_PATH.exists():
            shutil.rmtree(SCREENSHOTS_PATH)
        report_file = REPORT_OUTPUT_PATH / REPORT_FILENAME
        if report_file.exists():
            report_file.unlink()

    # ─── HOOKS DE BEHAVE ───

    def start_feature(self, feature):
        """Registra el inicio de una feature."""
        if not REPORT_ENABLED:
            return
        self._current_feature = {
            'name': feature.name,
            'tags': [str(tag) for tag in feature.tags],
            'description': feature.description,
            'status': 'passed',
            'scenarios': [],
            'start_time': datetime.now()
        }

    def end_feature(self, feature):
        """Registra el fin de una feature."""
        if not REPORT_ENABLED or self._current_feature is None:
            return
        self._current_feature['end_time'] = datetime.now()
        self._current_feature['duration'] = (
            self._current_feature['end_time'] - self._current_feature['start_time']
        ).total_seconds()

        has_failed = any(
            s['status'] == 'failed' for s in self._current_feature['scenarios']
        )
        self._current_feature['status'] = 'failed' if has_failed else 'passed'
        self.features.append(self._current_feature)
        self._current_feature = None

    def start_scenario(self, scenario):
        """Registra el inicio de un escenario."""
        if not REPORT_ENABLED:
            return
        self._current_scenario = {
            'name': scenario.name,
            'tags': [str(tag) for tag in scenario.tags],
            'status': 'passed',
            'steps': [],
            'start_time': datetime.now(),
            'error_message': None
        }

    def end_scenario(self, scenario):
        """Registra el fin de un escenario."""
        if not REPORT_ENABLED or self._current_scenario is None:
            return
        self._current_scenario['end_time'] = datetime.now()
        self._current_scenario['duration'] = (
            self._current_scenario['end_time'] - self._current_scenario['start_time']
        ).total_seconds()

        if self._current_feature:
            self._current_feature['scenarios'].append(self._current_scenario)
        self._current_scenario = None

    def record_step(self, step, screenshot_path=None):
        """Registra el resultado de un step."""
        if not REPORT_ENABLED or self._current_scenario is None:
            return

        step_data = {
            'keyword': step.keyword,
            'name': step.name,
            'status': step.status.name if hasattr(step.status, 'name') else str(step.status),
            'duration': step.duration if hasattr(step, 'duration') else 0,
            'screenshot': screenshot_path,
            'error_message': None
        }

        if step_data['status'] == 'failed':
            self._current_scenario['status'] = 'failed'
            error_msg = ''
            if hasattr(step, 'error_message') and step.error_message:
                error_msg = str(step.error_message)
            elif hasattr(step, 'exception') and step.exception:
                error_msg = str(step.exception)
            step_data['error_message'] = error_msg
            self._current_scenario['error_message'] = error_msg

        self._current_scenario['steps'].append(step_data)

    def capture_screenshot(self, page, step, scenario):
        """Captura screenshot si corresponde según configuración."""
        if not REPORT_ENABLED:
            return None

        step_status = step.status.name if hasattr(step.status, 'name') else str(step.status)

        if SCREENSHOT_ONLY_ON_FAILURE and step_status != 'failed':
            return None
        if not SCREENSHOT_ON_EACH_STEP and step_status != 'failed':
            return None

        try:
            self._step_counter += 1
            safe_scenario = "".join(
                c if c.isalnum() or c in (' ', '-', '_') else '_'
                for c in scenario.name
            )[:50]
            filename = f"{self._step_counter:04d}_{safe_scenario}_{step_status}.png"
            filepath = SCREENSHOTS_PATH / filename

            page.screenshot(path=str(filepath), full_page=False)
            return str(filepath)
        except Exception:
            return None

    def finalize(self):
        """Finaliza la recopilación y genera el reporte."""
        if not REPORT_ENABLED:
            return

        self.end_time = datetime.now()
        self._generate_html_report()

        if REPORT_OPEN_AFTER_RUN:
            import webbrowser
            webbrowser.open(REPORT_FILE_PATH.as_uri())

    # ══════════════════════════════════════════════════════════
    # GENERACIÓN DEL HTML
    # ══════════════════════════════════════════════════════════

    def _generate_html_report(self):
        """Genera el archivo HTML completo del reporte."""
        config = self.config
        apariencia = config.get('apariencia', {})
        proyecto = config.get('proyecto', {})
        equipo = config.get('equipo', {})
        reporte_cfg = config.get('reporte', {})

        stats = self._calculate_stats()
        html = self._build_html(apariencia, proyecto, equipo, reporte_cfg, stats)

        with open(REPORT_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(html)

    def _calculate_stats(self):
        """Calcula estadísticas generales de la ejecución."""
        total_scenarios = sum(len(f['scenarios']) for f in self.features)
        passed_scenarios = sum(
            1 for f in self.features for s in f['scenarios'] if s['status'] == 'passed'
        )
        failed_scenarios = sum(
            1 for f in self.features for s in f['scenarios'] if s['status'] == 'failed'
        )
        skipped_scenarios = total_scenarios - passed_scenarios - failed_scenarios

        total_steps = sum(
            len(s['steps']) for f in self.features for s in f['scenarios']
        )
        passed_steps = sum(
            1 for f in self.features for s in f['scenarios']
            for st in s['steps'] if st['status'] == 'passed'
        )
        failed_steps = sum(
            1 for f in self.features for s in f['scenarios']
            for st in s['steps'] if st['status'] == 'failed'
        )

        total_duration = (
            (self.end_time - self.start_time).total_seconds()
            if self.start_time and self.end_time else 0
        )
        pass_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0

        return {
            'total_features': len(self.features),
            'total_scenarios': total_scenarios,
            'passed_scenarios': passed_scenarios,
            'failed_scenarios': failed_scenarios,
            'skipped_scenarios': skipped_scenarios,
            'total_steps': total_steps,
            'passed_steps': passed_steps,
            'failed_steps': failed_steps,
            'total_duration': total_duration,
            'pass_rate': pass_rate
        }

    def _build_html(self, apariencia, proyecto, equipo, reporte_cfg, stats):
        """Construye el HTML completo del reporte."""
        c = {
            'pri': apariencia.get('color_primario', '#6366f1'),
            'sec': apariencia.get('color_secundario', '#8b5cf6'),
            'ok': apariencia.get('color_exito', '#10b981'),
            'fail': apariencia.get('color_fallo', '#ef4444'),
            'skip': apariencia.get('color_omitido', '#f59e0b'),
            'bg': apariencia.get('color_fondo', '#0f172a'),
            'card': apariencia.get('color_tarjeta', '#1e293b'),
            'txt': apariencia.get('color_texto', '#f8fafc'),
            'txt2': apariencia.get('color_texto_secundario', '#94a3b8'),
            'font': apariencia.get('fuente', "'Inter', 'Segoe UI', system-ui, sans-serif"),
        }

        titulo = reporte_cfg.get('titulo', 'Reporte de Pruebas Automatizadas')
        thumb_w = reporte_cfg.get('thumbnail_width', '320px')
        duration_str = self._format_duration(stats['total_duration'])
        timestamp = self.start_time.strftime('%d/%m/%Y %H:%M:%S') if self.start_time else 'N/A'

        features_html = self._build_features_html(c, thumb_w)
        donut_svg = self._build_donut_svg(stats, c)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: {c['font']};
            background: {c['bg']};
            color: {c['txt']};
            line-height: 1.6;
            min-height: 100vh;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}

        /* ─── HEADER ─── */
        .report-header {{
            background: linear-gradient(135deg, {c['pri']}20, {c['sec']}20);
            border: 1px solid {c['pri']}40;
            border-radius: 16px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }}
        .report-header::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, {c['pri']}, {c['sec']});
        }}
        .header-title {{
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, {c['pri']}, {c['sec']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .header-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }}
        .meta-item {{ display: flex; flex-direction: column; gap: 0.25rem; }}
        .meta-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {c['txt2']};
            font-weight: 500;
        }}
        .meta-value {{ font-size: 0.95rem; font-weight: 500; }}

        /* ─── STATS CARDS ─── */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: {c['card']};
            border: 1px solid {c['pri']}20;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}
        .stat-number {{ font-size: 2.2rem; font-weight: 700; line-height: 1; margin-bottom: 0.5rem; }}
        .stat-label {{ font-size: 0.8rem; color: {c['txt2']}; text-transform: uppercase; letter-spacing: 0.05em; }}

        /* ─── CHARTS ─── */
        .charts-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .chart-card {{
            background: {c['card']};
            border: 1px solid {c['pri']}20;
            border-radius: 12px;
            padding: 1.5rem;
        }}
        .chart-title {{ font-size: 1rem; font-weight: 600; margin-bottom: 1rem; }}
        .donut-chart {{ display: flex; align-items: center; justify-content: center; gap: 2rem; }}
        .donut-svg {{ width: 160px; height: 160px; }}
        .donut-legend {{ display: flex; flex-direction: column; gap: 0.75rem; }}
        .legend-item {{ display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; }}
        .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
        .progress-bar {{
            height: 12px;
            background: {c['bg']};
            border-radius: 6px;
            overflow: hidden;
            display: flex;
        }}
        .progress-segment {{ height: 100%; transition: width 0.5s ease; }}
        .progress-label {{
            display: flex;
            justify-content: space-between;
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: {c['txt2']};
        }}

        /* ─── FEATURES ─── */
        .section-title {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .feature-card {{
            background: {c['card']};
            border: 1px solid {c['pri']}20;
            border-radius: 12px;
            margin-bottom: 1rem;
            overflow: hidden;
        }}
        .feature-header {{
            padding: 1.25rem 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
            user-select: none;
        }}
        .feature-header:hover {{ background: {c['pri']}10; }}
        .feature-info {{ display: flex; align-items: center; gap: 0.75rem; flex: 1; }}
        .feature-name {{ font-weight: 600; font-size: 1rem; }}
        .tag {{
            font-size: 0.7rem;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background: {c['pri']}30;
            color: {c['pri']};
            font-weight: 500;
        }}
        .feature-badge {{
            padding: 0.3rem 0.8rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .badge-passed {{ background: {c['ok']}20; color: {c['ok']}; }}
        .badge-failed {{ background: {c['fail']}20; color: {c['fail']}; }}
        .chevron {{
            transition: transform 0.3s;
            color: {c['txt2']};
            font-size: 1.2rem;
        }}
        .chevron.open {{ transform: rotate(180deg); }}
        .feature-body {{ display: none; padding: 0 1.5rem 1.5rem; }}
        .feature-body.open {{ display: block; }}

        /* ─── SCENARIOS ─── */
        .scenario-card {{
            background: {c['bg']};
            border: 1px solid {c['pri']}15;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            overflow: hidden;
        }}
        .scenario-header {{
            padding: 1rem 1.25rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }}
        .scenario-header:hover {{ background: {c['pri']}08; }}
        .scenario-info {{ display: flex; align-items: center; gap: 0.6rem; }}
        .scenario-name {{ font-weight: 500; font-size: 0.9rem; }}
        .scenario-duration {{ font-size: 0.75rem; color: {c['txt2']}; }}
        .scenario-body {{ display: none; padding: 0 1.25rem 1.25rem; }}
        .scenario-body.open {{ display: block; }}
        .error-box {{
            background: {c['fail']}10;
            border: 1px solid {c['fail']}40;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            font-size: 0.8rem;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            color: {c['fail']};
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 200px;
            overflow-y: auto;
        }}

        /* ─── STEPS ─── */
        .steps-list {{ display: flex; flex-direction: column; gap: 0.4rem; }}
        .step-item {{
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 0.6rem 0.8rem;
            border-radius: 8px;
            font-size: 0.85rem;
            transition: background 0.2s;
        }}
        .step-item:hover {{ background: {c['pri']}08; }}
        .step-icon {{
            flex-shrink: 0;
            width: 22px; height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 700;
        }}
        .step-passed .step-icon {{ background: {c['ok']}20; color: {c['ok']}; }}
        .step-failed .step-icon {{ background: {c['fail']}20; color: {c['fail']}; }}
        .step-skipped .step-icon {{ background: {c['skip']}20; color: {c['skip']}; }}
        .step-content {{ flex: 1; }}
        .step-keyword {{ font-weight: 600; color: {c['pri']}; }}
        .step-screenshot {{ margin-top: 0.5rem; }}
        .step-screenshot img {{
            max-width: {thumb_w};
            border-radius: 8px;
            border: 1px solid {c['pri']}30;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .step-screenshot img:hover {{
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }}

        /* ─── MODAL ─── */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.92);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        .modal-overlay.active {{ display: flex; }}
        .modal-overlay img {{
            max-width: 90%; max-height: 90%;
            border-radius: 8px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}

        /* ─── FOOTER ─── */
        .report-footer {{
            text-align: center;
            padding: 2rem;
            color: {c['txt2']};
            font-size: 0.8rem;
            border-top: 1px solid {c['pri']}20;
            margin-top: 3rem;
        }}

        /* ─── RESPONSIVE ─── */
        @media (max-width: 768px) {{
            .container {{ padding: 1rem; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .header-title {{ font-size: 1.4rem; }}
            .donut-chart {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="report-header">
            <div>
                <h1 class="header-title">{titulo}</h1>
                <p style="color: {c['txt2']}; margin-top: 0.5rem; font-size: 0.9rem;">
                    {proyecto.get('descripcion', '')}
                </p>
            </div>
            <div class="header-meta">
                <div class="meta-item">
                    <span class="meta-label">Proyecto</span>
                    <span class="meta-value">{proyecto.get('nombre', 'N/A')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Ambiente</span>
                    <span class="meta-value">{proyecto.get('ambiente', 'N/A')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Equipo</span>
                    <span class="meta-value">{equipo.get('nombre', 'N/A')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Ingeniero QA</span>
                    <span class="meta-value">{equipo.get('ingeniero_qa', 'N/A')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Fecha de Ejecución</span>
                    <span class="meta-value">{timestamp}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Duración Total</span>
                    <span class="meta-value">{duration_str}</span>
                </div>
            </div>
        </div>

        <!-- STATS CARDS -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" style="color: {c['pri']};">{stats['total_features']}</div>
                <div class="stat-label">Features</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: {c['pri']};">{stats['total_scenarios']}</div>
                <div class="stat-label">Escenarios</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: {c['ok']};">{stats['passed_scenarios']}</div>
                <div class="stat-label">Exitosos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: {c['fail']};">{stats['failed_scenarios']}</div>
                <div class="stat-label">Fallidos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: {c['skip']};">{stats['skipped_scenarios']}</div>
                <div class="stat-label">Omitidos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: {c['pri']};">{stats['pass_rate']:.1f}%</div>
                <div class="stat-label">Tasa de Éxito</div>
            </div>
        </div>

        <!-- CHARTS -->
        <div class="charts-section">
            <div class="chart-card">
                <div class="chart-title">Distribución de Resultados</div>
                <div class="donut-chart">
                    {donut_svg}
                    <div class="donut-legend">
                        <div class="legend-item">
                            <div class="legend-dot" style="background: {c['ok']};"></div>
                            <span>Exitosos ({stats['passed_scenarios']})</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-dot" style="background: {c['fail']};"></div>
                            <span>Fallidos ({stats['failed_scenarios']})</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-dot" style="background: {c['skip']};"></div>
                            <span>Omitidos ({stats['skipped_scenarios']})</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">Progreso General</div>
                <div style="display: flex; flex-direction: column; justify-content: center; height: calc(100% - 2rem);">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <span style="font-size: 3rem; font-weight: 700; color: {c['pri']};">{stats['pass_rate']:.0f}%</span>
                        <p style="color: {c['txt2']}; font-size: 0.85rem; margin-top: 0.25rem;">de escenarios exitosos</p>
                    </div>
                    <div>
                        <div class="progress-bar">
                            <div class="progress-segment" style="width: {self._pct(stats['passed_scenarios'], stats['total_scenarios'])}%; background: {c['ok']};"></div>
                            <div class="progress-segment" style="width: {self._pct(stats['failed_scenarios'], stats['total_scenarios'])}%; background: {c['fail']};"></div>
                            <div class="progress-segment" style="width: {self._pct(stats['skipped_scenarios'], stats['total_scenarios'])}%; background: {c['skip']};"></div>
                        </div>
                        <div class="progress-label">
                            <span>{stats['passed_scenarios']} exitosos</span>
                            <span>{stats['failed_scenarios']} fallidos</span>
                            <span>{stats['skipped_scenarios']} omitidos</span>
                        </div>
                    </div>
                    <div style="margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.4rem; font-weight: 600;">{stats['total_steps']}</div>
                            <div style="font-size: 0.75rem; color: {c['txt2']};">Total Steps</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.4rem; font-weight: 600;">{duration_str}</div>
                            <div style="font-size: 0.75rem; color: {c['txt2']};">Duración</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FEATURES -->
        <div class="features-section">
            <h2 class="section-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{c['pri']}" stroke-width="2">
                    <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
                    <rect x="9" y="3" width="6" height="4" rx="2"/>
                </svg>
                Detalle por Feature
            </h2>
            {features_html}
        </div>

        <!-- FOOTER -->
        <div class="report-footer">
            <p>Generado por <strong>{equipo.get('empresa', 'QA Team')}</strong> &middot; {equipo.get('ingeniero_qa', '')} &middot; {timestamp}</p>
            <p style="margin-top: 0.25rem;">Behave + Playwright &middot; v{proyecto.get('version', '1.0.0')}</p>
        </div>
    </div>

    <!-- MODAL SCREENSHOTS -->
    <div class="modal-overlay" id="screenshotModal">
        <img id="modalImage" src="" alt="Screenshot">
    </div>

    <script>
        document.querySelectorAll('.feature-header').forEach(h => {{
            h.addEventListener('click', () => {{
                h.nextElementSibling.classList.toggle('open');
                h.querySelector('.chevron').classList.toggle('open');
            }});
        }});
        document.querySelectorAll('.scenario-header').forEach(h => {{
            h.addEventListener('click', () => {{
                h.nextElementSibling.classList.toggle('open');
                h.querySelector('.chevron').classList.toggle('open');
            }});
        }});
        const modal = document.getElementById('screenshotModal');
        const modalImg = document.getElementById('modalImage');
        document.querySelectorAll('.step-screenshot img').forEach(img => {{
            img.addEventListener('click', e => {{
                e.stopPropagation();
                modalImg.src = img.src;
                modal.classList.add('active');
            }});
        }});
        modal.addEventListener('click', () => modal.classList.remove('active'));
        document.addEventListener('keydown', e => {{ if (e.key === 'Escape') modal.classList.remove('active'); }});
    </script>
</body>
</html>"""

    # ══════════════════════════════════════════════════════════
    # BUILDERS AUXILIARES
    # ══════════════════════════════════════════════════════════

    def _build_features_html(self, c, thumb_w):
        """Genera el HTML para todas las features."""
        parts = []
        for feature in self.features:
            badge_cls = 'badge-passed' if feature['status'] == 'passed' else 'badge-failed'
            badge_txt = 'PASSED' if feature['status'] == 'passed' else 'FAILED'
            tags_html = ''.join(f'<span class="tag">@{t}</span>' for t in feature.get('tags', []))
            dur = self._format_duration(feature.get('duration', 0))
            scenarios_html = self._build_scenarios_html(feature['scenarios'], c, thumb_w)

            parts.append(f"""
            <div class="feature-card">
                <div class="feature-header">
                    <div class="feature-info">
                        <span class="feature-badge {badge_cls}">{badge_txt}</span>
                        <span class="feature-name">{feature['name']}</span>
                        <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">{tags_html}</div>
                    </div>
                    <div style="display:flex;align-items:center;gap:1rem;">
                        <span style="font-size:0.8rem;color:#94a3b8;">{dur}</span>
                        <span class="chevron">&#9660;</span>
                    </div>
                </div>
                <div class="feature-body">{scenarios_html}</div>
            </div>""")
        return '\n'.join(parts)

    def _build_scenarios_html(self, scenarios, c, thumb_w):
        """Genera el HTML de los escenarios."""
        parts = []
        for sc in scenarios:
            badge_cls = 'badge-passed' if sc['status'] == 'passed' else 'badge-failed'
            badge_txt = 'PASSED' if sc['status'] == 'passed' else 'FAILED'
            dur = self._format_duration(sc.get('duration', 0))
            tags_html = ''.join(f'<span class="tag">@{t}</span>' for t in sc.get('tags', []))

            error_html = ''
            if sc['status'] == 'failed' and sc.get('error_message'):
                safe_err = (
                    sc['error_message']
                    .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                )
                error_html = f'<div class="error-box">{safe_err}</div>'

            steps_html = self._build_steps_html(sc['steps'], c)

            parts.append(f"""
                <div class="scenario-card">
                    <div class="scenario-header">
                        <div class="scenario-info">
                            <span class="feature-badge {badge_cls}">{badge_txt}</span>
                            <span class="scenario-name">{sc['name']}</span>
                            {tags_html}
                        </div>
                        <div style="display:flex;align-items:center;gap:0.75rem;">
                            <span class="scenario-duration">{dur}</span>
                            <span class="chevron">&#9660;</span>
                        </div>
                    </div>
                    <div class="scenario-body">
                        {error_html}
                        <div class="steps-list">{steps_html}</div>
                    </div>
                </div>""")
        return '\n'.join(parts)

    def _build_steps_html(self, steps, c):
        """Genera el HTML de los steps."""
        parts = []
        for step in steps:
            status = step['status']
            if status == 'passed':
                icon, css_cls = '&#10003;', 'step-passed'
            elif status == 'failed':
                icon, css_cls = '&#10007;', 'step-failed'
            else:
                icon, css_cls = '&#8722;', 'step-skipped'

            screenshot_html = ''
            if step.get('screenshot'):
                img_src = self._screenshot_to_src(step['screenshot'])
                if img_src:
                    screenshot_html = f'<div class="step-screenshot"><img src="{img_src}" alt="Screenshot" loading="lazy"></div>'

            parts.append(f"""
                <div class="step-item {css_cls}">
                    <div class="step-icon">{icon}</div>
                    <div class="step-content">
                        <span class="step-keyword">{step['keyword']} </span>
                        <span class="step-text">{step['name']}</span>
                        {screenshot_html}
                    </div>
                </div>""")
        return '\n'.join(parts)

    def _build_donut_svg(self, stats, c):
        """Genera gráfico SVG de dona."""
        total = stats['total_scenarios']
        if total == 0:
            return '<svg class="donut-svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="#334155" stroke-width="20"/></svg>'

        circumference = 2 * 3.14159 * 40
        passed_d = (stats['passed_scenarios'] / total) * circumference
        failed_d = (stats['failed_scenarios'] / total) * circumference
        skipped_d = (stats['skipped_scenarios'] / total) * circumference

        return f"""<svg class="donut-svg" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" stroke="#334155" stroke-width="20"/>
            <circle cx="50" cy="50" r="40" fill="none" stroke="{c['ok']}" stroke-width="20"
                stroke-dasharray="{passed_d} {circumference}" stroke-dashoffset="0"
                transform="rotate(-90 50 50)"/>
            <circle cx="50" cy="50" r="40" fill="none" stroke="{c['fail']}" stroke-width="20"
                stroke-dasharray="{failed_d} {circumference}" stroke-dashoffset="-{passed_d}"
                transform="rotate(-90 50 50)"/>
            <circle cx="50" cy="50" r="40" fill="none" stroke="{c['skip']}" stroke-width="20"
                stroke-dasharray="{skipped_d} {circumference}" stroke-dashoffset="-{passed_d + failed_d}"
                transform="rotate(-90 50 50)"/>
            <text x="50" y="50" text-anchor="middle" dy="0.35em"
                font-size="16" font-weight="700" fill="{c['txt']}">{stats['pass_rate']:.0f}%</text>
        </svg>"""

    @staticmethod
    def _screenshot_to_src(screenshot_path):
        """Convierte screenshot a base64 data URI para portabilidad."""
        try:
            path = Path(screenshot_path)
            if path.exists():
                with open(path, 'rb') as f:
                    data = base64.b64encode(f.read()).decode('utf-8')
                return f"data:image/png;base64,{data}"
        except Exception:
            pass
        return None

    @staticmethod
    def _format_duration(seconds):
        """Formatea duración en formato legible."""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            m = int(seconds // 60)
            s = seconds % 60
            return f"{m}m {s:.0f}s"

    @staticmethod
    def _pct(value, total):
        """Porcentaje seguro."""
        return (value / total * 100) if total > 0 else 0
