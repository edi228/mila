/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount, useEnv } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

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
        progressValue: { type: Number, optional: true },
        progressMax: { type: Number, optional: true },
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

// ─── Property Table ──────────────────────────────────────────────────────────
class ImmoPropertyTable extends Component {
    static template = "maono_real_estate.ImmoPropertyTable";
    static props = {
        properties: Array,
        currencySymbol: String,
        onOpenProperty: Function,
    };

    setup() {
        this.state = useState({
            filter: "all",
            sortField: "name",
            sortDir: "asc",
            search: "",
        });
    }

    get filteredProperties() {
        let props = this.props.properties;
        // Filter by state
        if (this.state.filter !== "all") {
            props = props.filter((p) => p.state === this.state.filter);
        }
        // Search
        if (this.state.search) {
            const q = this.state.search.toLowerCase();
            props = props.filter(
                (p) =>
                    p.name.toLowerCase().includes(q) ||
                    p.tenant_name.toLowerCase().includes(q) ||
                    p.building_name.toLowerCase().includes(q) ||
                    (p.ref || "").toLowerCase().includes(q)
            );
        }
        // Sort
        const { sortField, sortDir } = this.state;
        props = [...props].sort((a, b) => {
            let va = a[sortField] ?? "";
            let vb = b[sortField] ?? "";
            if (typeof va === "string") va = va.toLowerCase();
            if (typeof vb === "string") vb = vb.toLowerCase();
            if (va < vb) return sortDir === "asc" ? -1 : 1;
            if (va > vb) return sortDir === "asc" ? 1 : -1;
            return 0;
        });
        return props;
    }

    setFilter(filter) {
        this.state.filter = filter;
    }

    setSort(field) {
        if (this.state.sortField === field) {
            this.state.sortDir = this.state.sortDir === "asc" ? "desc" : "asc";
        } else {
            this.state.sortField = field;
            this.state.sortDir = "asc";
        }
    }

    getSortIcon(field) {
        if (this.state.sortField !== field) return "fa-sort";
        return this.state.sortDir === "asc" ? "fa-sort-asc" : "fa-sort-desc";
    }

    getStateBadgeClass(state) {
        const classes = {
            occupied: "immo-prop-badge--occupied",
            available: "immo-prop-badge--available",
            works: "immo-prop-badge--works",
            suspended: "immo-prop-badge--suspended",
        };
        return "immo-prop-badge " + (classes[state] || "immo-prop-badge--muted");
    }

    getStateLabel(state) {
        const labels = {
            occupied: "Occupé",
            available: "Disponible",
            works: "Travaux",
            suspended: "Suspendu",
        };
        return labels[state] || state;
    }

    getTypeLabel(type) {
        const labels = {
            apartment: "Appartement",
            house: "Maison",
            studio: "Studio",
            office: "Bureau",
            commercial: "Commercial",
            land: "Terrain",
            parking: "Parking",
        };
        return labels[type] || type || "—";
    }

    formatAmount(amount) {
        if (!amount) return "—";
        return (
            new Intl.NumberFormat("fr-FR").format(Math.round(amount)) +
            " " +
            this.props.currencySymbol
        );
    }

    onSearchInput(ev) {
        this.state.search = ev.target.value;
    }
}

// ─── Building Grid ────────────────────────────────────────────────────────────
class ImmoBuildingGrid extends Component {
    static template = "maono_real_estate.ImmoBuildingGrid";
    static props = {
        buildings: Array,
        currencySymbol: String,
        onOpenProperty: Function,
    };

    getBadgeClass(state) {
        const classes = {
            occupied: "immo-building-badge--occupied",
            available: "immo-building-badge--available",
            works: "immo-building-badge--works",
            suspended: "immo-building-badge--suspended",
        };
        return "immo-building-badge " + (classes[state] || "immo-building-badge--muted");
    }

    getOccupationBarClass(rate) {
        if (rate >= 80) return "immo-occ-bar--green";
        if (rate >= 50) return "immo-occ-bar--orange";
        return "immo-occ-bar--red";
    }

    formatAmount(amount) {
        if (!amount) return "—";
        return (
            new Intl.NumberFormat("fr-FR").format(Math.round(amount)) +
            " " +
            this.props.currencySymbol
        );
    }

    getTooltip(prop) {
        const parts = [];
        if (prop.tenant_name) parts.push("Locataire : " + prop.tenant_name);
        if (prop.rent_amount) parts.push("Loyer : " + this.formatAmount(prop.rent_amount));
        return parts.join(" | ") || prop.name;
    }
}

// ─── Main Dashboard ──────────────────────────────────────────────────────────
export class ImmoDashboard extends Component {
    static template = "maono_real_estate.ImmoDashboard";
    static components = { ImmoKpiCard, ImmoAlertItem, ImmoPropertyTable, ImmoBuildingGrid };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            data: null,
            lastRefresh: null,
            refreshInterval: 60,
            activeTab: "leases", // leases | properties | buildings
        });

        this._refreshTimer = null;

        // Pre-bind KPI navigation callbacks
        this.kpiCallbacks = {
            allProperties: () =>
                this._doAction({
                    res_model: "re.property",
                    name: "Biens immobiliers",
                }),
            occupiedProperties: () =>
                this._doAction({
                    res_model: "re.property",
                    domain: [["state", "=", "occupied"]],
                    name: "Biens occupés",
                }),
            allLeases: () =>
                this._doAction({
                    res_model: "re.lease",
                    domain: [["lease_state", "=", "3_progress"]],
                    name: "Baux actifs",
                }),
            unpaidInvoices: () =>
                this._doAction({
                    res_model: "account.move",
                    domain: [
                        ["move_type", "=", "out_invoice"],
                        ["state", "=", "posted"],
                        ["payment_state", "not in", ["paid", "in_payment"]],
                        ["invoice_date_due", "<", new Date().toISOString().split("T")[0]],
                    ],
                    name: "Factures impayées",
                }),
            allPenalties: () =>
                this._doAction({
                    res_model: "re.penalty",
                    domain: [["state", "not in", ["cancelled", "invoiced"]]],
                    name: "Pénalités actives",
                }),
        };

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

    setTab(tab) {
        this.state.activeTab = tab;
    }

    // ── Core action helper ──
    _doAction({ res_model, res_id = undefined, domain = undefined, name = undefined }) {
        const act = {
            type: "ir.actions.act_window",
            res_model,
            views: res_id ? [[false, "form"]] : [[false, "list"], [false, "form"]],
        };
        if (res_id !== undefined) act.res_id = res_id;
        if (domain !== undefined) act.domain = domain;
        if (name !== undefined) act.name = name;
        this.action.doAction(act);
    }

    // ── Navigation helpers ──
    openLease(id) { this._doAction({ res_model: "re.lease", res_id: id }); }
    openProperty(id) { this._doAction({ res_model: "re.property", res_id: id }); }
    openService(id) { this._doAction({ res_model: "re.property.service", res_id: id }); }
    openAllLeases() { this.kpiCallbacks.allLeases(); }
    openAllServices() { this._doAction({ res_model: "re.property.service", name: "Interventions" }); }
    navigateAlert(alert) { this._doAction({ res_model: alert.link_model, res_id: alert.link_id }); }

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

    // KPI occupancy fraction label
    getOccupancyLabel(kpis) {
        return `${kpis.occupied} / ${kpis.total_properties}`;
    }
}

registry.category("actions").add("maono_real_estate.immo_dashboard", ImmoDashboard);
