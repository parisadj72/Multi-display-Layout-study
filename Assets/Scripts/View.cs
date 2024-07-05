using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class View : MonoBehaviour, ISelectHandler
{
    private Toggle toggle;
    private string icon;

    private Boolean isOn;
    private Boolean isInteractable;

    public Boolean disabledAtStartup = true;

    private void Awake()
    {
        InitializeView();

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

    public string Icon
    {
        get { return icon; }
        set { icon = value; }
    }

    private void InitializeView()
    {
        toggle = GetComponent<Toggle>();
        icon = GetImage();
        //print(icon);
        isInteractable = toggle.interactable;
        IsOn = toggle.isOn;
    }
    public void SetStatus()
    {
        IsOn = toggle.isOn;
    }

    public void TurnOn(Boolean isOn)
    {
        IsOn = isOn;
        toggle.interactable = isOn;
        toggle.isOn = isOn;
        //print("Interaction enabled: " + toggle.interactable);
    }

    public string GetImage()
    {
        RawImage rawImage = null;
        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            //print(child.gameObject);
            if (child.gameObject.name == "On")
            {
                rawImage = child.GetComponentInChildren<RawImage>();
                //print(rawImage.texture);
            }
        }
        return rawImage.texture.name;
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }

    public void OnSelect(BaseEventData eventData)
    {
        if (IsOn)
        {
            //print("view clicked. Disable now?");
            StartCoroutine(WaitUntilOff());
        }
    }

    IEnumerator WaitUntilOff()
    {
        yield return new WaitUntil(() => !IsOn);

        //print("view is now off");
        DisableInteraction();
    }
}
