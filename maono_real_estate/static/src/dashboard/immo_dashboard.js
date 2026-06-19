/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { formatMonetary } from "@web/views/fields/formatters";

// ─── KPI Card ────────────────────────────────────────────────────────────────
class ImmoKpiCard extends Component {
    static template = "maono_real_estate.ImmoKpiCard";
    static props = {
        icon: String,
        label: String,
        value: [String, Number],
        subtitle: { type: String, optional: true },
        color: { type: String, optional: true },
        onClick: { type: Function, optional: true },
    };
}

// ─── Alert Item ──────────────────────────────────────────────────────────────
class ImmoAlertItem extends Component {
    static template = "maono_real_estate.ImmoAlertItem";
    static props = {
        alert: Object,
        onNavigate: Function,
    };
    navigate() {
        this.props.onNavigate(this.props.alert);
    }
}

// ─── Main Dashboard ──────────────────────────────────────────────────────────
export class ImmoDashboard extends Component {
    static template = "maono_real_estate.ImmoDashboard";
    static components = { ImmoKpiCard, ImmoAlertItem };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            data: null,
            lastRefresh: null,
            refreshInterval: 60,
        });

        this._refreshTimer = null;

        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            this._startAutoRefresh();
        });

        onWillUnmount(() => {
            this._stopAutoRefresh();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const data = await this.orm.call("re.dashboard", "get_dashboard_data", []);
            this.state.data = data;
            this.state.refreshInterval = data.refresh_interval;
            this.state.lastRefresh = new Date().toLocaleTimeString("fr-FR");
        } catch (e) {
            this.notification.add("Erreur lors du chargement du dashboard", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async manualRefresh() {
        this._stopAutoRefresh();
        await this.loadData();
        this._startAutoRefresh();
        this.notification.add("Dashboard actualisé", { type: "success", sticky: false });
    }

    _startAutoRefresh() {
        this._stopAutoRefresh();
        const interval = (this.state.refreshInterval || 60) * 1000;
        this._refreshTimer = setInterval(() => this.loadData(), interval);
    }

    _stopAutoRefresh() {
        if (this._refreshTimer) {
            clearInterval(this._refreshTimer);
            this._refreshTimer = null;
        }
    }

    // ── Navigation helpers ──
    openLease(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "re.lease",
            res_id: id,
            views: [[false, "form"]],
        });
    }

    openProperty(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "re.property",
            res_id: id,
            views: [[false, "form"]],
        });
    }

    openService(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "re.property.service",
            res_id: id,
            views: [[false, "form"]],
        });
    }

    openAllLeases() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "re.lease",
            views: [[false, "list"], [false, "form"]],
            domain: [["lease_state", "=", "3_progress"]],
            name: "Baux actifs",
        });
    }

    openAllServices() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "re.property.service",
            views: [[false, "list"], [false, "form"]],
            name: "Interventions",
        });
    }

    navigateAlert(alert) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: alert.link_model,
            res_id: alert.link_id,
            views: [[false, "form"]],
        });
    }

    // ── Formatters ──
    formatAmount(amount) {
        if (!this.state.data) return "0";
        const sym = this.state.data.currency_symbol || "";
        return `${new Intl.NumberFormat("fr-FR").format(Math.round(amount))} ${sym}`;
    }

    getDaysLabel(days) {
        if (days === null || days === undefined) return "—";
        if (days < 0) return `${Math.abs(days)}j dépassé`;
        return `${days}j restants`;
    }

    getStateLabel(state) {
        const labels = {
            "1_draft": "Devis",
            "3_progress": "Actif",
            "4_paused": "Suspendu",
            "5_renewed": "Renouvelé",
            "6_churn": "Résilié",
        };
        return labels[state] || state;
    }

    getServiceStateLabel(state) {
        const labels = {
            draft: "Brouillon",
            submitted: "Soumis",
            approved: "Approuvé",
            in_progress: "En cours",
            validation: "Validation",
            done: "Validé",
            cancelled: "Annulé",
        };
        return labels[state] || state;
    }

    getPriorityStars(priority) {
        const n = parseInt(priority) || 0;
        return "★".repeat(n) + "☆".repeat(3 - n);
    }
}

registry.category("actions").add("maono_real_estate.immo_dashboard", ImmoDashboard);
