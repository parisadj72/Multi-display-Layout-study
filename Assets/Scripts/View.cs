using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit.UI;

public class View : MonoBehaviour, ISelectHandler, IDeselectHandler
{
    public GameObject viewWindow;
    private Toggle toggle;
    private Boolean isOn;
    private Boolean hasBeenClicked;

    private void Start()
    {
        toggle = viewWindow.GetComponent<Toggle>();
        IsOn = toggle.isOn;
        HasBeenClicked = false;
        //print("IsOn = " + IsOn);
        //TurnOn(true);
        //DisableInteraction();
        //EventTest();
    }

    public Boolean IsOn
    {
        get { return isOn; }
        set { isOn = value; }
    }

    public Boolean HasBeenClicked
    {
        get { return hasBeenClicked; }
        set { hasBeenClicked = value; }
    }

    public void TurnOn(bool isOn)
    {
        toggle.isOn = isOn;
        IsOn = isOn;
        toggle.interactable = isOn;
    }

    public void SetStatus()
    {
        IsOn = toggle.isOn;
    }

    public void TurnOff()
    {
        TurnOn(false);
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }

    public void EventTest()
    {
        //print("Event activated");
        SetStatus();
        //print("Window is on? " + IsOn);
    }

    public void OnSelect(BaseEventData eventData)
    {
        print(this.gameObject.name + " was selected");
        //TurnOff();
        //DisableInteraction();
    }

    public void OnDeselect(BaseEventData eventData)
    {
        print("Deselected");
    }
}
