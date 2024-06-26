using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class ViewScript : MonoBehaviour
{
    public Boolean disabledAtStartup = true;
    private Toggle toggle;
    private Boolean isOn;
    private Boolean hasBeenClicked = false;

    private void Awake()
    {
        toggle = GetComponent<Toggle>();
        SetStatus();

        if (disabledAtStartup)
        {
            DisableInteraction();
        }
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

    public void TurnOn()
    {
        IsOn = true;
        //toggle.interactable = true;
        toggle.isOn = true;
    }
    public void TurnOff()
    {
        IsOn = false;
        toggle.isOn = false;
    }

    public void SetStatus()
    {
        IsOn = toggle.isOn;
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }
    public void EnableInteraction()
    {
        toggle.interactable = true;
    }

    public void OnSelect(BaseEventData eventData)
    {
        if (IsOn && !hasBeenClicked)
        {
            print("view clicked. Disable now?");
            StartCoroutine(WaitUntilOff());
        }
    }

    IEnumerator WaitUntilOff()
    {
        yield return new WaitUntil(() => !IsOn);

        print("view is now off");
        DisableInteraction();
    }
}
