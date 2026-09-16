/** @odoo-module **/

import { Component, useState, onMounted, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * Holiday Badge Component
 * 
 * Shows a badge indicator when a date is a holiday.
 * Used in calendar views and date fields.
 */
export class HolidayBadge extends Component {
    static template = "zarvan_calendar.HolidayBadge";
    static props = {
        date: { type: String },
        companyId: { type: Number, optional: true },
    };
    
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            isHoliday: false,
            holidayName: '',
            holidayType: '',
            isLoading: true,
        });
        
        onMounted(() => this.checkHoliday());
        onWillUpdateProps(() => this.checkHoliday());
    }
    
    async checkHoliday() {
        if (!this.props.date) {
            this.state.isLoading = false;
            return;
        }
        
        try {
            const holidays = await this.orm.searchRead('jalaali.holiday', [
                ['gregorian_date', '=', this.props.date],
                ['is_active', '=', true],
            ], ['name', 'holiday_type']);
            
            if (holidays.length > 0) {
                this.state.isHoliday = true;
                this.state.holidayName = holidays[0].name;
                this.state.holidayType = holidays[0].holiday_type;
            } else {
                this.state.isHoliday = false;
                this.state.holidayName = '';
                this.state.holidayType = '';
            }
            
            this.state.isLoading = false;
        } catch (error) {
            console.error('Error checking holiday:', error);
            this.state.isLoading = false;
        }
    }
    
    get badgeClass() {
        if (!this.state.isHoliday) return '';
        
        switch (this.state.holidayType) {
            case 'national': return 'badge-national';
            case 'lunar': return 'badge-lunar';
            case 'fixed': return 'badge-fixed';
            case 'regional': return 'badge-regional';
            default: return 'badge-default';
        }
    }
}

registry.category("components").add("HolidayBadge", HolidayBadge);
