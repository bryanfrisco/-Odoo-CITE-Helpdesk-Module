/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";
import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    useRef,
    useState,
} from "@odoo/owl";

const REFRESH_INTERVAL_MS = 60000;

export class CiteDashboard extends Component {
    static template = "cite_helpdesk.Dashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ data: null, slaPeriod: "month" });
        this.charts = {};
        this.statusCanvas = useRef("statusCanvas");
        this.trendCanvas = useRef("trendCanvas");

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.loadData();
        });
        onMounted(() => {
            this.renderCharts();
            this.timer = setInterval(() => this.refresh(), REFRESH_INTERVAL_MS);
        });
        onWillUnmount(() => {
            clearInterval(this.timer);
            this.destroyCharts();
        });
    }

    async loadData() {
        this.state.data = await this.orm.call(
            "helpdesk.ticket",
            "get_cite_dashboard_data",
            [this.state.slaPeriod]
        );
    }

    async onSlaPeriodChange(ev) {
        this.state.slaPeriod = ev.target.value;
        const sla = await this.orm.call(
            "helpdesk.ticket",
            "get_cite_sla_compliance",
            [this.state.slaPeriod]
        );
        if (this.state.data) {
            this.state.data.sla = sla;
        }
    }

    async refresh() {
        await this.loadData();
        this.renderCharts();
    }

    destroyCharts() {
        for (const chart of Object.values(this.charts)) {
            chart.destroy();
        }
        this.charts = {};
    }

    renderCharts() {
        this.destroyCharts();
        const data = this.state.data;
        if (!data) {
            return;
        }
        if (this.statusCanvas.el) {
            this.charts.status = new Chart(this.statusCanvas.el, {
                type: "doughnut",
                data: {
                    labels: data.by_status.labels,
                    datasets: [{
                        data: data.by_status.counts,
                        backgroundColor: [
                            "#875A7B", "#4285f4", "#fbbc05", "#ea8b35",
                            "#34a853", "#46a3a3", "#5b8def", "#e25563",
                            "#9aa0a6", "#c5a3cb", "#7bc043",
                        ],
                    }],
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: { legend: { position: "right" } },
                },
            });
        }
        if (this.trendCanvas.el) {
            this.charts.trend = new Chart(this.trendCanvas.el, {
                type: "line",
                data: {
                    labels: data.trend.labels,
                    datasets: [
                        {
                            label: "Created",
                            data: data.trend.created,
                            borderColor: "#4285f4",
                            backgroundColor: "#4285f4",
                            tension: 0.3,
                        },
                        {
                            label: "Solved",
                            data: data.trend.solved,
                            borderColor: "#34a853",
                            backgroundColor: "#34a853",
                            tension: 0.3,
                        },
                    ],
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: { legend: { position: "top" } },
                    scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
                },
            });
        }
    }

    openDomain(key, title) {
        const viewIds = this.state.data.views;
        this.action.doAction({
            type: "ir.actions.act_window",
            name: title,
            res_model: "helpdesk.ticket",
            domain: this.state.data.domains[key],
            views: [[viewIds.tree, "list"], [viewIds.form, "form"]],
            target: "current",
        });
    }

    openTicket(ticketId) {
        const viewIds = this.state.data.views;
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "helpdesk.ticket",
            res_id: ticketId,
            views: [[viewIds.form, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("cite_helpdesk.dashboard", CiteDashboard);
