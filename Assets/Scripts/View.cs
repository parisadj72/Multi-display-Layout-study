using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit.UI;

public class View : MonoBehaviour
{
    public GameObject viewWindow;
    private Boolean isOn;

    private void Start()
    {
        DisableInteraction();
    }

    public Boolean IsOn
    {
        get { return isOn; }
        set { isOn = value; }
    }

    public void SetState()
    {
        IsOn = viewWindow.GetComponent<Toggle>().isOn;
        print("Window is: " + IsOn);
    }

    public void TurnOn(bool isOn)
    {
        IsOn = isOn;
        viewWindow.GetComponent<Toggle>().isOn = isOn;
        GetComponent<TrackedDeviceGraphicRaycaster>().enabled = isOn;
    }

    public void TurnOff()
    {
        if (isOn && GetComponent<TrackedDeviceGraphicRaycaster>().enabled)
        {
            IsOn = false;
            DisableInteraction();
        }
    }

    public void DisableInteraction()
    {
        GetComponent<TrackedDeviceGraphicRaycaster>().enabled = false;
    }
}
