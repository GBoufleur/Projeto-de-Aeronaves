'''
This script holds input dictionaries for several aircraft
which can be used as starting point for new designs.
'''

# GENERAL IMPORTS
import numpy as np
from .constants import ft2m, gravity, nm2m, lb2N

#=================================================

def standard_airplane(name='crusair1'):
    '''
    The standard parameters refer to the Fokker 100, but they could be redefined for
    any new aircraft.
    '''

    if name == 'crusair1':

        # This model was taken from measuring the 3D view from
        # https://www.icas.org/ICAS_ARCHIVE/ICAS1988/ICAS-88-1.6.2.pdf
        # Obert, E. The Aerodynamic Development of the Fokker 100
        
        inputs = {'type': 'transport', # Can be 'transport', 'fighter', or 'general'

              'S_w' : 393.531, # Wing area [m2]
              'AR_w' : 8.974,  # Wing aspect ratio
              'taper_w' : 0.129, # Wing taper ratio
              'sweep_w' : 0.55, # Wing sweep [rad]
              'dihedral_w' : 0.104, # Wing dihedral [rad]
              'xr_w' : 21.905, # Longitudinal position of the wing (with respect to the fuselage nose) [m]
              'zr_w' : -1.4, # Vertical position of the wing (with respect to the fuselage nose) [m]
              'tcr_w' : 0.13, # t/c of the root section of the wing
              'tct_w' : 0.10, # t/c of the tip section of the wing

              'Cht' : 0.749, # Horizontal tail volume coefficient
              'Lc_h' : 3.606, # Non-dimensional lever of the horizontal tail (lever/wing_mac)
              'AR_h' : 4.817, # HT aspect ratio
              'taper_h' : 0.239, # HT taper ratio
              'sweep_h' : 0.675, # HT sweep [rad]
              'dihedral_h' : 0.128, # HT dihedral [rad]
              'zr_h' : 1.581, # Vertical position of the HT [m]
              'tcr_h' : 0.1, # t/c of the root section of the HT
              'tct_h' : 0.1, # t/c of the tip section of the HT
              'eta_h' : 1.0, # Dynamic pressure factor of the HT (0.9 for conventional tail or 1.0 for T-tail)

              'Cvt' : 0.071, # Vertical tail volume coefficient
              'Lb_v' : 0.51, # Non-dimensional lever of the vertical tail (lever/wing_span)
              'AR_v' : 2.055, # VT aspect ratio
              'taper_v' : 0.247, # VT taper ratio
              'sweep_v' : 0.802, # VT sweep [rad]
              'zr_v' : 3.087, # Vertical position of the VT [m]
              'tcr_v' : 0.12, # t/c of the root section of the VT
              'tct_v' : 0.12, # t/c of the tip section of the VT

              'L_f' : 66.820, # Fuselage length [m]
              'D_f' : 5.610, # Fuselage diameter [m]

              'x_n' : 23.575, # Longitudinal position of the nacelle frontal face [m]
              'y_n' : 9.329, # Lateral position of the nacelle centerline [m]
              'z_n' : -2.26, # Vertical position of the nacelle centerline [m]
              'L_n' : 5.736, # Nacelle length [m]
              'D_n' : 3.887, # Nacelle diameter [m]

              'n_engines' : 2, # Number of engines
              'n_engines_under_wing' : 0, # Number of engines installed under the wing
              'engine' : {'model' : 'Howe turbofan', # Check engineTSFC function for options
                          #'model' : 'Raymer turbofan', # Check engineTSFC function for options
                          'BPR' : 3.04, # Engine bypass ratio
                          #'weight' : 1500*gravity, # Single engine weight [N] (Can also be omitted to let designTool estimate it)
                          #'Tmax' : 13850*lb2N, # Single engine maximum thrust at sea level [N] (Can also be omitted to let designTool estimate it)
                          'C_ref' : 0.70/3600, # Reference thrust-specific fuel consumption [1/s] (Can also be omitted to let designTool estimate it)
                          'altitude_ref': 35000*ft2m, # Altitude that corresponds to the given TSFC [m]
                          'Mach_ref': 0.73, # Mach that corresponds to the given TSFC
                          },

              'x_nlg' : 5.766, # Longitudinal position of the nose landing gear [m]
              'x_mlg' : 33.54, # Longitudinal position of the main landing gear [m]
              'y_mlg' : 4.898, # Lateral position of the main landing gear [m]
              'z_lg' : -3.939, # Vertical position of the landing gear [m]
              'x_tailstrike' : 55.946, # Longitudinal position of critical tailstrike point [m]
              'z_tailstrike' : -2.9, # Vertical position of critical tailstrike point [m]

              'c_tank_c_w' : 0.4, # Fraction of the wing chord occupied by the fuel tank
              'x_tank_c_w' : 0.2, # Fraction of the wing chord where fuel tank starts
              'b_tank_b_w_start' : 0.0, # Fraction of the wing semi-span where fuel tank starts
              'b_tank_b_w_end' : 0.95, # Fraction of the wing semi-span where fuel tank ends

              'clmax_w' : 1.8, # Maximum lift coefficient of wing airfoil
              'k_korn' : 0.91, # Airfoil technology factor for Korn equation (wave drag)

              'flap_type' : 'single slotted',  # Flap type
              'c_flap_c_wing' : 0.147009, # Fraction of the wing chord occupied by flaps
              'b_flap_b_wing' : 0.533343, # Fraction of the wing span occupied by flaps (including fuselage portion)

              'slat_type' : 'flap', # Slat type
              'c_slat_c_wing' : 0.152007, # Fraction of the wing chord occupied by slats
              'b_slat_b_wing' : 0.740334, # Fraction of the wing span occupied by slats

              'c_ail_c_wing' : 0.272016, # Fraction of the wing chord occupied by aileron
              'b_ail_b_wing' : 0.262576, # Fraction of the wing span occupied by aileron

              'h_ground' : 10.668, # Distance to the ground for ground effect computation [m]
              'k_exc_drag' : 0.06, # Excrescence drag factor applied to systems (Torenbeek Tab F-5.7)

              'winglet' : True, # Add winglet

              'altitude_takeoff' : 0.0, # Altitude for takeoff computation [m]
              'distance_takeoff' : 2900.0, # Required takeoff distance [m]
              'deltaISA_takeoff' : 0.0, # Variation from ISA standard temperature [ºC]

              'altitude_landing' : 0.0, # Altitude for landing computation [m]
              'distance_landing' : 1900.0, # Required landing distance [m]
              'deltaISA_landing' : 0.0, # Variation from ISA standard temperature [ºC]
              'MLW_frac' : 40100/43090, # Max Landing Weight / Max Takeoff Weight

              'altitude_cruise' : 10668.0, # Cruise altitude for design mission [m]
              'Mach_cruise' : 0.85, # Cruise Mach number for design mission
              'range_cruise' : 14445600.0, # Cruise range for design mission [m]

              'altitude_maxcruise' : 35000*ft2m, # Altitude for high-speed cruise [m]
              'Mach_maxcruise' : 0.77, # Mach for high-speed cruise [m]

              'time_loiter' : 2700.0, # Loiter time [s]
              'altitude_loiter' : 457.2, # Loiter altitude [m]

              'altitude_altcruise' : 457.2, # Alternative cruise altitude [m]
              'Mach_altcruise' : 0.4, # Alternative cruise Mach number
              'range_altcruise' : 370400.0, # Alternative cruise range [m]

              'W_payload' : 320*100*gravity, # Payload weight for design mission [N]
              'xcg_payload' : 14.4, # Longitudinal position of the Payload center of gravity [m]
              'W_maxpayload' : 11242*gravity, # Maximum payload weight [N]

              'W_crew' : 5*91*gravity, # Crew weight [N]
              'xcg_crew' : 2.5, # Longitudinal position of the Crew center of gravity [m]

              'block_range' : 400*nm2m, # Block range [m]
              'block_time' : (1.0 + 2*40/60)*3600, # Block time [s]
              'n_captains' : 1, # Number of captains in flight
              'n_copilots' : 1, # Number of copilots in flight

              'rho_fuel' : 804, # Fuel density kg/m3 (This is Jet A-1)

              'W0_guess' : 280000*gravity, # Guess for MTOW

              'We_fudge' : 1000 # Fudge factor to adjust empty weight
              }
        
    elif name == 'crusair2':

        # This is just a placeholder to register the student airplane.

        inputs = {'type': 'transport', # Can be 'transport', 'fighter', or 'general'

              'S_w' : 393.531, # Wing area [m2]
              'AR_w' : 8.974,  # Wing aspect ratio
              'taper_w' : 0.129, # Wing taper ratio
              'sweep_w' : 0.55, # Wing sweep [rad]
              'dihedral_w' : 0.104, # Wing dihedral [rad]
              'xr_w' : 21.905, # Longitudinal position of the wing (with respect to the fuselage nose) [m]
              'zr_w' : -1.4, # Vertical position of the wing (with respect to the fuselage nose) [m]
              'tcr_w' : 0.13, # t/c of the root section of the wing
              'tct_w' : 0.10, # t/c of the tip section of the wing

              'Cht' : 0.749, # Horizontal tail volume coefficient
              'Lc_h' : 3.606, # Non-dimensional lever of the horizontal tail (lever/wing_mac)
              'AR_h' : 4.817, # HT aspect ratio
              'taper_h' : 0.239, # HT taper ratio
              'sweep_h' : 0.675, # HT sweep [rad]
              'dihedral_h' : 0.128, # HT dihedral [rad]
              'zr_h' : 1.581, # Vertical position of the HT [m]
              'tcr_h' : 0.1, # t/c of the root section of the HT
              'tct_h' : 0.1, # t/c of the tip section of the HT
              'eta_h' : 1.0, # Dynamic pressure factor of the HT (0.9 for conventional tail or 1.0 for T-tail)

              'Cvt' : 0.071, # Vertical tail volume coefficient
              'Lb_v' : 0.51, # Non-dimensional lever of the vertical tail (lever/wing_span)
              'AR_v' : 2.055, # VT aspect ratio
              'taper_v' : 0.247, # VT taper ratio
              'sweep_v' : 0.802, # VT sweep [rad]
              'zr_v' : 3.087, # Vertical position of the VT [m]
              'tcr_v' : 0.12, # t/c of the root section of the VT
              'tct_v' : 0.12, # t/c of the tip section of the VT

              'L_f' : 66.54, # Fuselage length [m]
              'D_f' : 6.11, # Fuselage diameter [m]

              'x_n' : 23.575, # Longitudinal position of the nacelle frontal face [m]
              'y_n' : 9.329, # Lateral position of the nacelle centerline [m]
              'z_n' : -2.26, # Vertical position of the nacelle centerline [m]
              'L_n' : 5.736, # Nacelle length [m]
              'D_n' : 3.887, # Nacelle diameter [m]

              'n_engines' : 2, # Number of engines
              'n_engines_under_wing' : 0, # Number of engines installed under the wing
              'engine' : {'model' : 'Howe turbofan', # Check engineTSFC function for options
                          #'model' : 'Raymer turbofan', # Check engineTSFC function for options
                          'BPR' : 3.04, # Engine bypass ratio
                          #'weight' : 1500*gravity, # Single engine weight [N] (Can also be omitted to let designTool estimate it)
                          #'Tmax' : 13850*lb2N, # Single engine maximum thrust at sea level [N] (Can also be omitted to let designTool estimate it)
                          'C_ref' : 0.70/3600, # Reference thrust-specific fuel consumption [1/s] (Can also be omitted to let designTool estimate it)
                          'altitude_ref': 35000*ft2m, # Altitude that corresponds to the given TSFC [m]
                          'Mach_ref': 0.73, # Mach that corresponds to the given TSFC
                          },

              'x_nlg' : 5.766, # Longitudinal position of the nose landing gear [m]
              'x_mlg' : 33.54, # Longitudinal position of the main landing gear [m]
              'y_mlg' : 4.898, # Lateral position of the main landing gear [m]
              'z_lg' : -3.939, # Vertical position of the landing gear [m]
              'x_tailstrike' : 55.946, # Longitudinal position of critical tailstrike point [m]
              'z_tailstrike' : -2.9, # Vertical position of critical tailstrike point [m]

              'c_tank_c_w' : 0.4, # Fraction of the wing chord occupied by the fuel tank
              'x_tank_c_w' : 0.2, # Fraction of the wing chord where fuel tank starts
              'b_tank_b_w_start' : 0.0, # Fraction of the wing semi-span where fuel tank starts
              'b_tank_b_w_end' : 0.95, # Fraction of the wing semi-span where fuel tank ends

              'clmax_w' : 1.8, # Maximum lift coefficient of wing airfoil
              'k_korn' : 0.91, # Airfoil technology factor for Korn equation (wave drag)

              'flap_type' : 'double slotted',  # Flap type
              'c_flap_c_wing' : 0.147009, # Fraction of the wing chord occupied by flaps
              'b_flap_b_wing' : 0.533343, # Fraction of the wing span occupied by flaps (including fuselage portion)

              'slat_type' : 'Leading Edge Slats', # Slat type
              'c_slat_c_wing' : 0.152007, # Fraction of the wing chord occupied by slats
              'b_slat_b_wing' : 0.740334, # Fraction of the wing span occupied by slats

              'c_ail_c_wing' : 0.272016, # Fraction of the wing chord occupied by aileron
              'b_ail_b_wing' : 0.262576, # Fraction of the wing span occupied by aileron

              'h_ground' : 10.668, # Distance to the ground for ground effect computation [m]
              'k_exc_drag' : 0.06, # Excrescence drag factor applied to systems (Torenbeek Tab F-5.7)

              'winglet' : True, # Add winglet

              'altitude_takeoff' : 0.0, # Altitude for takeoff computation [m]
              'distance_takeoff' : 2900.0, # Required takeoff distance [m]
              'deltaISA_takeoff' : 0.0, # Variation from ISA standard temperature [ºC]

              'altitude_landing' : 0.0, # Altitude for landing computation [m]
              'distance_landing' : 1900.0, # Required landing distance [m]
              'deltaISA_landing' : 0.0, # Variation from ISA standard temperature [ºC]
              'MLW_frac' : 40100/43090, # Max Landing Weight / Max Takeoff Weight

              'altitude_cruise' : 10668.0, # Cruise altitude for design mission [m]
              'Mach_cruise' : 0.85, # Cruise Mach number for design mission
              'range_cruise' : 14445600.0, # Cruise range for design mission [m]

              'altitude_maxcruise' : 35000*ft2m, # Altitude for high-speed cruise [m]
              'Mach_maxcruise' : 0.77, # Mach for high-speed cruise [m]

              'time_loiter' : 2700.0, # Loiter time [s]
              'altitude_loiter' : 457.2, # Loiter altitude [m]

              'altitude_altcruise' : 457.2, # Alternative cruise altitude [m]
              'Mach_altcruise' : 0.4, # Alternative cruise Mach number
              'range_altcruise' : 370400.0, # Alternative cruise range [m]

              'W_payload' : 320*100*gravity, # Payload weight for design mission [N]
              'xcg_payload' : 14.4, # Longitudinal position of the Payload center of gravity [m]
              'W_maxpayload' : 11242*gravity, # Maximum payload weight [N]

              'W_crew' : 8*91*gravity, # Crew weight [N]
              'xcg_crew' : 2.5, # Longitudinal position of the Crew center of gravity [m]

              'block_range' : 400*nm2m, # Block range [m]
              'block_time' : (1.0 + 2*40/60)*3600, # Block time [s]
              'n_captains' : 1, # Number of captains in flight
              'n_copilots' : 1, # Number of copilots in flight

              'rho_fuel' : 804, # Fuel density kg/m3 (This is Jet A-1)

              'W0_guess' : 280000*gravity, # Guess for MTOW

              'We_fudge' : 1000 # Fudge factor to adjust empty weight
              }

    airplane = {'inputs':inputs}

    return airplane
