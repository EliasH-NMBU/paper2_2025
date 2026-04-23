import subprocess
import tempfile
import os
import re
import unicodedata


def normalize(f: str) -> str:
    # --- Normalize Unicode form ---
    f = unicodedata.normalize("NFKD", f)

    # --- Replace known math/logical Unicode operators ---
    replacements = {
        "−": "-",   
        "–": "-",   
        "—": "-",   
        "“": '"', "”": '"',
        "‘": "'", "’": "'",
        "×": "*",
        "·": "*",
        "…": "...",
        "→": "->",
        "⇒": "->",
        "↔": "<->",
        "≤": "<=",
        "≥": ">=",
        "≠": "!=",
        "¬": "!",
        "∧": "&",
        "∨": "|",
        "&&": "&",
        "||": "|",
        "≠": "!=",
    }
    for k, v in replacements.items():
        f = f.replace(k, v)

    # --- Collapse repeated whitespace ---
    f = re.sub(r"\s+", " ", f).strip()

    return f


def responseHandler(model, f1, f2):

    # Create temporary .smv file
    with tempfile.NamedTemporaryFile(suffix=".smv", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(model)
        tmp_path = tmp.name

    try:
        try:
            result = subprocess.run(
                ["nuxmv.exe", tmp_path],
                capture_output=True,
                text=True,
                timeout=45       # seconds
            )
        except subprocess.TimeoutExpired:
            print("⏳ NuXMV timed out — returning empty")
            return

    finally:
        # Ensure temporary file is always removed
        os.remove(tmp_path)

    output = result.stdout
    error_output = result.stderr

    if "is true" in output:
        return True
    elif "is false" in output:
        return False
    else:
        print("⚠️ Unexpected NuXMV output format")
        print("---- STDOUT ----")
        print("Reference:", f1, "\n", "Generated:", f2)
        print("---- STDERR ----")
        print(error_output)
        print("----------------")
        return 


def check_equivalence_ltl(formula1, formula2):

    f1 = normalize(formula1)
    f2 = normalize(formula2)

    model = f"""
    MODULE main
    VAR
        RES : boolean;
        CONDITION_EXP : boolean;
        MODE_EXP : boolean;
        STOP_CONDITION : boolean;

    LTLSPEC !( ({f1}) <-> ({f2}) )
    """
    return responseHandler(model, f1, f2)   


def check_equivalence_master(formula1, formula2):
    
    f1 = normalize(formula1)
    f2 = normalize(formula2)

    model = f"""
    MODULE main

    IVAR
      classifier : {{0, 1, 2}};
      distance_to_target : 0..10;

    VAR
      alert : boolean;
      halt : boolean;
      slowdown : boolean;
      turnoffUVC : boolean;
      OpState : {{0, 1, 2, 3}};

    DEFINE
      dgt_3 := distance_to_target > 3;
      dgt_7 := distance_to_target > 7;

    LTLSPEC ({f1}) <-> ({f2})
    """

    return responseHandler(model, f1, f2)


def check_equivalence_rover(formula1, formula2):

    f1 = normalize(formula1)
    f2 = normalize(formula2)

    model = f"""
    MODULE main
    VAR
    battery : 0..100;
    chargePosition : 0..100;
    recharge : boolean;
    goal : 0..100;
    pre_battery : 0..100;
    n : 1..100;
    plan : 0..100;
    chargeNeeded_var : 0..100;
    length_plan : 0..100;
    batteryFull : boolean;
    atGoal : boolean;
    Obstacle : boolean;
    currentPosition : 0..10;
    initialPosition : 0..100;
    currentPhysicalPosition : 0..100;
    start : 0..100;
    s0 : 0..100;
    x : 0..100;
    y : 0..100;
    obstacle : 0..10;
    Obstacle_currentPosition : boolean;
    speed : 0..100;
    removeGoalFromSet : boolean;

    LTLSPEC ({f1}) <-> ({f2})
    """
    return responseHandler(model, f1, f2)      


def check_equivalence_abzrover_extended(formula1, formula2):
    f1 = normalize(formula1)
    f2 = normalize(formula2)

    model = f"""
    MODULE main
    VAR
        currentPosition : 0..1000;
        obstacles : array 0..50 of boolean; -- presence map
        GSObstacles : array 0..50 of boolean;
        obstacleAccuracy : 0..100; -- percentage
        perturbationInput : 0..1000;
        prioritisedGoals : array 0..20 of 0..1000;
        chargers : array 0..10 of 0..1000;
        invalidMap : boolean;
        goal : 0..1000;
        safeLocation : 0..1000;
        recharge : boolean;
        atGoal : boolean;
        noplan : boolean;
        systemState : 0..10; -- encoded system-state finite set
        plan2C : array 0..100 of 0..1000;
        plan2D : array 0..100 of 0..1000;
        plans : array 0..20 of 0..1000;
        planTimeout : boolean;
        batteryLevel : 0..100;
        measuredBattery : 0..100;
        movementCommands : 0..20;
        velocityCommands : 0..20;
        solarPanelsOpen : boolean;
        batteryNeededToGoal : 0..100;
        batteryNeededToCharger : 0..100;
        communicationData : 0..20; -- encoded enum
        completed : boolean;
        noMoreViablePlans : boolean;
        failed2Reconnect : boolean;
        connectionStatus : 0..3; -- 0=ok 1=failed 2=reconnecting 3=timeout
        responseData : 0..1000;
        helperId : 0..50;
        location : 0..1000;
        failure : boolean;
        failureCause : 0..10; -- symbolic failure classification
        reboot : boolean;
        requestHelp : boolean;
        waitForHelpTimer : 0..1000;

    LTLSPEC ({f1}) <-> ({f2})
    """

    return responseHandler(model, f1, f2)


def check_equivalence_drone(formula1, formula2):
    f1 = normalize(formula1)
    f2 = normalize(formula2)

    model = f"""
    MODULE main
    VAR
        SimulationMode : boolean;
        SimulationModeRaspberry : boolean;
        SimulateCommunications : boolean;
        SimulatePackageSending : boolean;
        RealMode : boolean;
        SimulationLoopStart : boolean;
        SimulationLoopFinish : boolean;
        HILSimulationGazebo : boolean;
        JetsonFailureDetectionRunning : boolean;
        JetsonFailureTransitionToNucleo : boolean;
        NucleoOnline : boolean;
        NucleoFailureSwitchActiveNucleo : boolean;
        NucleoOneControl : boolean;
        SendNucleoOneControlMessage : boolean;
        NucleoTwoControl : boolean;
        SendNucleoTwoControlMessage : boolean;
        ActiveNucleoFailureDetectionRunning : boolean;
        ActiveNucleo : boolean;
        MonitorPowerConsumption : boolean;
        ReturnPowerConsumptionData : boolean;
        SimulateFailureTransition : boolean;
        SimulatePacketLoss : boolean;
        SimulationDataSaved : boolean;
        ServoMonitoring : boolean;
        BatteryMonitoring : boolean;
        UseRealTimeClock : boolean;
        AttitudeMonitoring : boolean;
        OverallSystemHealthMonitoring : boolean;
        PacketLossRate : 0..100;
        AcceptablePacketLoss : 0..100;
        ElectricSystemsHealthMonitoring : boolean;
        ControlLoopStartRaspberry : boolean;
        ControlLoopStartNucleo : boolean;
        ControlLoopFinish : boolean;
        RaspberryFailureDetectionRunning : boolean;
        EvaluateControllerPerformance : boolean;
        MeasureControlTransition : boolean;
        CollectHardwareExecutionTimes : boolean;
        AssessHardwareTimePerformance : boolean;
        ControlAlgorithmStart : boolean;
        ControlAlgorithmFinish : boolean;
        ControlLoopStart : boolean;
        MonitorGroundSpeed : boolean;
        SendGroundSpeedData : boolean;
        MonitorWindSpeed : boolean;
        SendWindSpeedData : boolean;
        MonitorPitotTube : boolean;
        SendPitotTubeData : boolean;
        MonitorAlphaVane : boolean;
        SendAlphaVaneData : boolean;
        MonitorBetaVane : boolean;
        SendBetaVaneData : boolean;
        MonitorServoMotors : boolean;
        SendServoMotorsData : boolean;
        MonitorTiltAngles : boolean;
        SendTiltAngleData : boolean;
        MonitorAccelerations : boolean;
        SendAccelerationsData : boolean;
        MonitorBarometerAltitude : boolean;
        SendBarometerAltitudeData : boolean;
        MonitorRow : boolean;
        SendRowData : boolean;
        MonitorPitch : boolean;
        SendPitchData : boolean;
        MonitorYaw : boolean;
        SendYawData : boolean;
        MonitorAccelerometerData : boolean;
        SendAccelerometerData : boolean;
        MonitorMagnetometerData : boolean;
        SendMagnetometerData : boolean;
        MonitorGyroscopeData : boolean;
        SendGyroscopeData : boolean;
        MonitorCompassData : boolean;
        SendCompassData : boolean;
        MonitorMotorRPM : boolean;
        SendMotorRPM : boolean;
        MonitorBoardStatus : boolean;
        SendBoardStatusData : boolean;
        MonitorGPSLatitude : boolean;
        MonitorGPSLongitude : boolean;
        MonitorGPSAltitude : boolean;
        MonitorGPSHomePosition : boolean;
        SendGPSData : boolean;
        SatelliteShadowing : boolean;
        NoReceptionLoS : boolean;
        SignalDiffraction : boolean;
        MultipathEffects : boolean;
        PositioningAccuracy : boolean;
        MonitorRTKData : boolean;
        SendRTKData : boolean;
        MonitorPropellerRPM : boolean;
        SendPropellerRPMData : boolean;
        MonitorComponentsTemeratures : boolean;
        SendComponentsTemperaturesData : boolean;
        MonitorInternalTemperature : boolean;
        SendInternalTemperatureData : boolean;
        MonitorBayAreaTemperature : boolean;
        SendBayAreaTemperatureData : boolean;
        MonitoringEnabledRaspberry : boolean;
        MonitorCommunicationQuality : boolean;
        MonitoringEnabled : boolean;
        ManageEnergySources : boolean;
        MonitorBatteryStatus : boolean;
        SendBatteryStatusData : boolean;
        MonitorBatteryLevel : boolean;
        SendBatteryLevelData : boolean;
        MonitorBatteryVoltage : boolean;
        SendBatteryVoltageData : boolean;
        MonitorVoltageBusConsumption : boolean;
        SendVoltageBusConsumptionData : boolean;
        AutonomousFlightMode : boolean;
        JetsonControl : boolean;
        JetsonControlDisplay : boolean;
        RemoteControlFlightMode : boolean;
        NulceoControl : boolean;
        NucleoControlDisplay : boolean;
        NucleoControl : boolean;
        FailsafeFlightMode : boolean;
        MonitorBrushlessCurrent : boolean;
        MonitorESCCurrent : boolean;
        MonitorServoMotorCurrent : boolean;
        DisplayCurrentController : boolean;
        SendBatteryDischargeRateData : boolean;
        MonitorBatteryDischargeRate : boolean;
        MonitorAngularVelocity : boolean;
        SendAngularVelocityData : boolean;
        NucleoOneFailureDetectionRunning : boolean;
        HILSimulation : boolean;
        NucleoTwoFailureDetectionRunning : boolean;
        true : boolean;
        false : boolean;

    LTLSPEC ({f1}) <-> ({f2})
    """

    return responseHandler(model, f1, f2)


def check_equivalence_pipeline(formula1, formula2):
    f1 = normalize(formula1)
    f2 = normalize(formula2)

    # variable_1, input integer variable_2, integer variable_3, bool variable_4, bool variable_5, integer constant variable_6, internal integer

    model = f"""
    MODULE main
    VAR
        variable_1 : 0..100; -- Input integer
        variable_2 : 0..100; -- Integer
        variable_3 : boolean; -- Boolean
        variable_4 : boolean; -- Boolean
        variable_5 : 0..100; -- Constant integer
        variable_6 : 0..100; -- Internal integer

    LTLSPEC ({f1}) <-> ({f2})
    """

    return responseHandler(model, f1, f2)


def check_equivalence_stlpipeline(formula1, formula2):
    f1 = normalize(formula1)
    f2 = normalize(formula2)

    # variable_1, input integer variable_2, integer variable_3, bool variable_4, bool variable_5, integer constant variable_6, internal integer

    model = f"""
    MODULE main
    VAR
        prop_1 : boolean; -- Boolean
        prop_2 : boolean; -- Boolean
        prop_3 : boolean; -- Boolean
        prop_4 : boolean; -- Boolean
        prop_5 : boolean; -- Boolean
        prop_6 : boolean; -- Boolean
        prop_7 : boolean; -- Boolean

    LTLSPEC ({f1}) <-> ({f2})
    """

    return responseHandler(model, f1, f2)


def check_equivalence_lungV(formula1, formula2):

    f1 = normalize(formula1)
    f2 = normalize(formula2)

    model = f"""
    MODULE main
    VAR
        ADCConnFailure : boolean;
        ADCError : 0..10;
        ADCRetries : 0..10;
        BreathingCycleStart : boolean;
        CONT : boolean;
        ExpiratoryPhaseEnd : boolean;
        ExpiratoryTime : 0..5000;
        ExpiratoryTriggerSensitivity : 0..100;
        Fail : boolean;
        FailSafeMode : boolean;
        FinalState : 0..10;
        GBPS : 0..1000;
        GUIConnected : boolean;
        GUIFailure : boolean;
        GUIResumeRequest : boolean;
        ITS_PCV : boolean;
        ITS_PSV : boolean;
        IToE : 0..10;
        IToE_AP : 0..10;
        InhaleTriggerSensitivityPCV : 0..100;
        InhaleTriggerSensitivityPSV : 0..100;
        ItoE : 0..10;
        ItoE_AP : 0..10;
        ItoE_PCV : 0..10;
        MaxP_insp : 0..100;
        MinPEEPAtmAnalyzer : 0..50;
        OutOfServiceWarning : boolean;
        PCVInspTimeEnd : boolean;
        PCVMode : boolean;
        PCVModeSelected : boolean;
        PSVMode : boolean;
        PSVModeSelected : boolean;
        P_insp : 0..100;
        P_inspAP : 0..100;
        P_inspPCV : 0..100;
        P_inspPSV : 0..100;
        Pass : boolean;
        PeakV_E : 0..1000;
        RM : boolean;
        RMButton : boolean;
        RR : 0..100;
        RR_AP : 0..100;
        RR_PCV : 0..100;
        Seconds : 0..10000;
        SelfTestFail : boolean;
        SelfTestMode : boolean;
        SensorUse : boolean;
        Skip : boolean;
        StandbyMode : boolean;
        StartUpDone : boolean;
        StartUpMode : boolean;
        V_E : 0..1000;
        _PRC_ : boolean;
        airSupplyConnected : boolean;
        alarmSettingsChanged : boolean;
        apnea : boolean;
        apneaAlarm : boolean;
        apneaLagTime : 0..10000;
        breathingCircuitConnected : boolean;
        breathingCycleDone : boolean;
        breathingCycleStart : boolean;
        breathingCycleTime : 0..10000;
        breathingTime : 0..10000;
        breathingTimerReset : boolean;
        buttonUnPressOr : boolean;
        checkCommsGUI : boolean;
        checkCommsSensors : boolean;
        checkCommsValves : boolean;
        confirmPSVParameters : boolean;
        defaultParamsLoaded : boolean;
        disableLeakCompensation : boolean;
        displayF : 0..100;
        displayO : 0..100;
        displayRR : 0..100;
        displayTV : 0..1000;
        dropPAW : boolean;
        enableLeakCompensation : boolean;
        enterAlarmThresholds : boolean;
        eraseLog : boolean;
        error : boolean;
        expClock : 0..10000;
        expirationPhaseEnd : boolean;
        expirationPhaseStart : boolean;
        expiratoryPause : boolean;
        expiratoryPauseButton : boolean;
        expiratoryPhase : boolean;
        expiratoryPhaseEnd : boolean;
        expiratoryState : boolean;
        gasSupplyFailure : boolean;
        highPriorityAlarm : boolean;
        inValveClose : boolean;
        inValveOpen : boolean;
        initDone : boolean;
        initFail : boolean;
        initStart : boolean;
        inspClock : 0..10000;
        inspiratoryPause : boolean;
        inspiratoryPauseButton : boolean;
        inspiratoryPhase : boolean;
        inspiratoryPhaseEnd : boolean;
        inspiratoryPhaseStart : boolean;
        inspiratoryPressure : 0..100;
        inspiratoryTime : 0..10000;
        leakCompensation : boolean;
        leakCompensationActive : boolean;
        leakCompensationEnable : boolean;
        loadLastParams : boolean;
        loadLog : boolean;
        logAlarmParams : boolean;
        logAlarmSettings : boolean;
        logCalibrationParams : boolean;
        logO : boolean;
        logParams : boolean;
        logPatientChange : boolean;
        logPowerSupply : boolean;
        logPreUseCheck : boolean;
        logVentilationParams : boolean;
        logVentilatorSettings : boolean;
        measureF : 0..100;
        measureO : 0..100;
        measurePSins : 0..100;
        measureRR : 0..100;
        measureTV : 0..1000;
        minExpiratoryTime : 0..10000;
        monitorInhaleTrigger : boolean;
        newPatient : boolean;
        off : boolean;
        operator : boolean;
        outValveClose : boolean;
        outValveOpen : boolean;
        paramAlarm_V : 0..100;
        paramMax_V : 0..100;
        paramMin_V : 0..100;
        param_V : 0..100;
        parametersStored : boolean;
        patientAttributesEntered : boolean;
        patientBreathTrigger : boolean;
        patientBreathingRequest : boolean;
        patientChanged : boolean;
        patientConnected : boolean;
        patientSafe : boolean;
        powerButton : boolean;
        powerConnected : boolean;
        powerFailure : boolean;
        powerOff : boolean;
        powerSupplyChanged : boolean;
        preUseCheckDone : boolean;
        pressureSensorConnFailure : boolean;
        pressureSensorError : boolean;
        pressureSensorRetries : 0..10;
        resumeVentilation : boolean;
        runSelfTest : boolean;
        saveLog : boolean;
        selfTestFailed : boolean;
        selfTestPassed : boolean;
        startMonitoring : boolean;
        startPCV : boolean;
        startPSV : boolean;
        startReportingHealthParams : boolean;
        stopVentilation : boolean;
        testAlarmsFail : boolean;
        testAlarmsPass : boolean;
        testAlarmsSkip : boolean;
        testFL : boolean;
        testLeaksFail : boolean;
        testLeaksPass : boolean;
        testLeaksSkip : boolean;
        testOxygenSensorFail : boolean;
        testOxygenSensorPass : boolean;
        testOxygenSensorSkip : boolean;
        testPSExpFail : boolean;
        testPSExpPass : boolean;
        testPSExpSkip : boolean;
        testPowerSwitchFail : boolean;
        testPowerSwitchPass : boolean;
        testPowerSwitchSkip : boolean;
        user : boolean;
        ventilating : boolean;
        ventilationOff : boolean;
        ventilationParamsAdjustable : boolean;
        ventilatorSettingsChanged : boolean;

    LTLSPEC ({f1}) <-> ({f2})
    """

    return responseHandler(model, f1, f2)


if __name__ == "__main__":

    # Example usage
    f1 = "H((classifier = 1 & dgt_7) -> (OpState = 1))"
    f2 = "H((classifier = 1) -> (dgt_7 -> (OpState = 1)))"

    g1 = "H((OpState=1 → (alert ∧ ¬slowdown ∧ ¬halt ∧ ¬turnoffUVC)))"
    g2 = "(H ((OpState = 1) -> ((((! slowdown) & (! halt)) & alert) & (! turnoffUVC))))"

    h1 = "(H ((classifier = 2) -> ((! dgt_3) -> (OpState = 3))))"
    h2 = "H(((classifier = 2) ∧ ¬dgt_3) → (OpState = 3))"

    equiv = check_equivalence_master(h1, h2)
    print("\nEquivalent:", equiv)

    equiv_rover = check_equivalence_rover(
        "H (atGoal -> (currentPosition = goal))", 
        "(H (atGoal -> (currentPosition = goal)))"
    )
    print("Rover Equivalent:", equiv_rover)

    pipeline = "(variable_3 → (variable_2 ≥ variable_5)) S (variable_1 > variable_6)"
    pipeline2 = "H((variable_1 > variable_6) -> H(variable_3 -> (variable_2 >= variable_5)))"
    p1 = normalize(pipeline)
    p2 = normalize(pipeline2)
    print("Normalize of Pipeline fault: ", p1)
    print("Normalize of Pipeline fault 2: ", p2)
    pipelineref = "(variable_3 → H(variable_2 ≥ variable_5))"


    print("pipeline from CSV, lungV: ")
    n1 = "(H (PCVMode -> (P_insp = P_inspPCV)))"
    n2 = "H(PCVMode → (P_insp = P_inspPCV))"
    print("LungV Equivalent:", check_equivalence_lungV(n1, n2))
