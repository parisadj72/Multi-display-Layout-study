using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit.UI;
using Varjo.XR;
using static UnityEngine.ParticleSystem;

public class View : MonoBehaviour, ISelectHandler, IDeselectHandler
{
    public Boolean disabledAtStartup = true;
    private Toggle toggle;
    private Boolean isOn;
    private Boolean hasBeenClicked = false;

    private void Start()
    {
        toggle = GetComponent<Toggle>();
        SetStatus();

        if (disabledAtStartup)
        {
            DisableInteraction();
        }
        //print("IsOn = " + IsOn);
        //TurnOn(true);
        //DisableInteraction();
        //EventTest();
    }

    public void Awake()
    {
        Start();
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
        //print("Toggle is: " + toggle.name);
        toggle.interactable = isOn;
        toggle.isOn = isOn;
        IsOn = isOn;
    }

    public void SetStatus()
    {
        IsOn = toggle.isOn;
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
        if (IsOn && !hasBeenClicked)
        {
            print("view clicked. Disable now?");
            StartCoroutine(WaitUntilOff());
            OnDeselect(eventData);
        }
        //print("the view is off...");
        //TurnOff();
        //DisableInteraction();
    }

    IEnumerator WaitUntilOff()
    {
        yield return new WaitUntil(() => !IsOn);

        print("view is now off");
        DisableInteraction();
    }


    public void OnDeselect(BaseEventData eventData)
    {
        //print("Deselected");
    }
}
