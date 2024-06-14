using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit.UI;

public class View : MonoBehaviour
{
    public GameObject viewWindow;
    private Boolean isOn;

    private void Start()
    {
        IsOn = viewWindow.GetComponent<Toggle>().isOn;
        TurnOn(true);
        //DisableInteraction();
    }

    public Boolean IsOn
    {
        get { return isOn; }
        set { isOn = value; }
    }

    public void TurnOn(bool isOn)
    {
        IsOn = isOn;
        GetComponent<Toggle>().isOn = isOn;
        GetComponent<TrackedDeviceGraphicRaycaster>().enabled = isOn;
    }

    public void SetStatus()
    {
        IsOn = viewWindow.GetComponent<Toggle>().isOn;
    }

    public void TurnOff()
    {
        TurnOn(false);
    }

    public void DisableInteraction()
    {
        GetComponent<TrackedDeviceGraphicRaycaster>().enabled = false;
    }

    public void EventTest()
    {
        print("Event activated");
        print("Window is on? " + IsOn);
    }
}
